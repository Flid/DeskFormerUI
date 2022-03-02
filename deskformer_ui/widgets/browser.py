from cefpython3 import cefpython as cef
import sdl2
import sdl2.ext
import logging
import sys
from kivy.uix.widget import Widget
from kivy.logger import Logger as log
from kivy.base import EventLoop
from threading import Thread, Lock
from kivy.properties import NumericProperty, ObjectProperty
from deskformer_ui.widgets.widgetbase import DFWidgetBase
from time import sleep
from kivy.graphics.vertex_instructions import Rectangle
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage, ImageData
from PIL import Image


class DFBrowserWidget(DFWidgetBase):
    # Mouse wheel fudge to enhance scrolling
    scroll_enhance = NumericProperty(40)
    # desired frame rate
    frame_rate = NumericProperty(30)

    # Define default background colour (black in this case)
    background_colour = ObjectProperty(sdl2.SDL_Color(255, 0, 0))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lock = Lock()
        # self._init_sdl2_rendering()
        self._initialized = False

        Clock.schedule_once(self._render_texture, 0)

    def _render_texture(self, *args):
        # keep it running
        Clock.schedule_once(self._render_texture, 0)

        if not self._initialized:
            self._init_sdl2_rendering()
            Thread(target=self._run, daemon=True).start()
            self._initialized = True

        with self._lock:
            if not self._renderHandler.texture:
                return

            # This part works, but overwrites the entire screen
            # sdl2.SDL_RenderCopy(
            #     self._renderer,
            #     self._renderHandler.texture,
            #     None,
            #     sdl2.SDL_Rect(
            #         int(self.x), int(self.y), int(self.width), int(self.height)
            #     ),
            # )
            # sdl2.SDL_RenderPresent(self._renderer)

            with self.canvas:
                # That doesn't work, since it expercts the Kivy texture
                Rectangle(
                    pos=self.pos, size=self.size, texture=self._renderHandler.texture
                )

    def _init_cef(self):
        # Initialise CEF for offscreen rendering
        cef.Initialize(
            settings={"windowless_rendering_enabled": True},
            switches={
                # Tweaking OSR performance by setting the same Chromium flags
                # as in upstream cefclient (Issue #240).
                "disable-surfaces": "",
                "disable-gpu": "",
                "disable-gpu-compositing": "",
                "enable-begin-frame-scheduling": "",
            },
        )
        self._window_info = cef.WindowInfo()
        self._window_info.SetAsOffscreen(0)
        log.info("cef initialised")

    def _init_sdl2_rendering(self):
        window_id = EventLoop.window._win.get_window_id()
        window = sdl2.video.SDL_GetWindowFromID(window_id)

        for _ in range(10):
            self._renderer = sdl2.SDL_CreateRenderer(
                window,
                -1,
                sdl2.render.SDL_RENDERER_SOFTWARE
                # sdl2.render.SDL_RENDERER_ACCELERATED
            )

            try:
                self._renderer.contents
                log.info("%s: Renderer initialized", self.__class__.__name__)
                break
            except ValueError:
                sleep(1)
        else:
            log.error("%s: Failed to initialize renderer", self.__class__.__name__)

        # Set-up the RenderHandler, passing in the SDL2 renderer
        self._renderHandler = RenderHandler(
            self._lock, self._renderer, self.width, self.height
        )

    def _run(self):
        self._init_cef()
        # self._init_sdl2_rendering()

        # Create the browser instance
        self._browser = cef.CreateBrowserSync(
            self._window_info,
            url="https://www.google.com/",
            settings={
                # Tweaking OSR performance (Issue #240)
                "windowless_frame_rate": self.frame_rate
            },
        )
        self._browser.SetClientHandler(LoadHandler())
        self._browser.SetClientHandler(self._renderHandler)
        # Must call WasResized at least once to let know CEF that
        # viewport size is available and that OnPaint may be called.
        self._browser.SendFocusEvent(True)
        self._browser.WasResized()

        # Begin the main rendering loop
        running = True
        # FPS debug variables
        frames = 0
        logging.debug("beginning rendering loop")
        resetFpsTime = True
        fpsTime = 0

        while running:
            # record when we started drawing this frame
            startTime = sdl2.timer.SDL_GetTicks()
            if resetFpsTime:
                fpsTime = sdl2.timer.SDL_GetTicks()
                resetFpsTime = False
            # Convert SDL2 events into CEF events (where appropriate)
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT or (
                    event.type == sdl2.SDL_KEYDOWN
                    and event.key.keysym.sym == sdl2.SDLK_ESCAPE
                ):
                    running = False
                    log.info("SDL2 QUIT event")
                    break

            cef.MessageLoopWork()
            frames += 1

            if sdl2.timer.SDL_GetTicks() - fpsTime > 1000:
                log.info("FPS: %d" % frames)
                frames = 0
                resetFpsTime = True

            # regulate frame rate
            if sdl2.timer.SDL_GetTicks() - startTime < 1000.0 / self.frame_rate:
                sdl2.timer.SDL_Delay(
                    (1000 // self.frame_rate) - (sdl2.timer.SDL_GetTicks() - startTime)
                )


class LoadHandler(object):
    """Simple handler for loading URLs."""

    def OnLoadingStateChange(self, is_loading, **_):
        if not is_loading:
            logging.info("Page loading complete")

    def OnLoadError(self, frame, failed_url, **_):
        if not frame.IsMain():
            return
        logging.error("Failed to load %s" % failed_url)


class RenderHandler(object):
    def __init__(self, lock, renderer, width, height):
        self._lock = lock
        self._renderer = renderer
        self._width = width
        self._height = height
        self.texture = None

    def GetViewRect(self, rect_out, **_):
        rect_out.extend([0, 0, self._width, self._height])
        return True

    def OnPaint(self, element_type, paint_buffer, **_):
        """
        Using the pixel data from CEF's offscreen rendering
        the data is converted by PIL into a SDL2 surface
        which can then be rendered as a SDL2 texture.
        """
        if element_type == cef.PET_VIEW:
            image = Image.frombuffer(
                "RGBA",
                (int(self._width), int(self._height)),
                paint_buffer.GetString(mode="rgba", origin="top-left"),
                "raw",
                "BGRA",
            )
            # Following PIL to SDL2 surface code from pysdl2 source.
            mode = image.mode
            rmask = gmask = bmask = amask = 0
            depth = None
            pitch = None
            if mode == "RGB":
                # 3x8-bit, 24bpp
                if sdl2.endian.SDL_BYTEORDER == sdl2.endian.SDL_LIL_ENDIAN:
                    rmask = 0x0000FF
                    gmask = 0x00FF00
                    bmask = 0xFF0000
                else:
                    rmask = 0xFF0000
                    gmask = 0x00FF00
                    bmask = 0x0000FF
                depth = 24
                pitch = self._width * 3
            elif mode in ("RGBA", "RGBX"):
                # RGBX: 4x8-bit, no alpha
                # RGBA: 4x8-bit, alpha
                if sdl2.endian.SDL_BYTEORDER == sdl2.endian.SDL_LIL_ENDIAN:
                    rmask = 0x00000000
                    gmask = 0x0000FF00
                    bmask = 0x00FF0000
                    if mode == "RGBA":
                        amask = 0xFF000000
                else:
                    rmask = 0xFF000000
                    gmask = 0x00FF0000
                    bmask = 0x0000FF00
                    if mode == "RGBA":
                        amask = 0x000000FF
                depth = 32
                pitch = self._width * 4
            else:
                logging.error("ERROR: Unsupported mode: %s" % mode)
                exit_app()

            pxbuf = image.tobytes()
            # Create surface
            surface = sdl2.SDL_CreateRGBSurfaceFrom(
                pxbuf,
                int(self._width),
                int(self._height),
                depth,
                int(pitch),
                rmask,
                gmask,
                bmask,
                amask,
            )

            with self._lock:
                if self.texture:
                    # free memory used by previous texture
                    sdl2.SDL_DestroyTexture(self.texture)

                self.texture = sdl2.SDL_CreateTextureFromSurface(
                    self._renderer, surface
                )

            sdl2.SDL_FreeSurface(surface)

        else:
            logging.warning("Unsupport element_type in OnPaint")

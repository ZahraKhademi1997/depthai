from .component import Component
from typing import Optional, Union, Tuple, Any, Dict
import depthai as dai
from ..replay import Replay


def setControl(control: dai.CameraControl,
               manualFocus: Optional[int] = None,
               afMode: Optional[dai.CameraControl.AutoFocusMode] = None,
               awbMode: Optional[dai.CameraControl.AutoWhiteBalanceMode] = None,
               sceneMode: Optional[dai.CameraControl.SceneMode] = None,
               antiBandingMode: Optional[dai.CameraControl.AntiBandingMode] = None,
               effectMode: Optional[dai.CameraControl.EffectMode] = None,
               sharpness: Optional[int] = None,
               lumaDenoise: Optional[int] = None,
               chromaDenoise: Optional[int] = None,

               ):
    if manualFocus is not None:
        control.setManualFocus(manualFocus)
    if afMode is not None:
        control.setAutoFocusMode(afMode)
    if awbMode is not None:
        control.setAutoWhiteBalanceMode(awbMode)
    if sceneMode is not None:
        control.setSceneMode(sceneMode)
    if antiBandingMode is not None:
        control.setAntiBandingMode(antiBandingMode)
    if effectMode is not None:
        control.setEffectMode(effectMode)
    if sharpness is not None:
        control.setSharpness(sharpness)
    if lumaDenoise is not None:
        control.setLumaDenoise(lumaDenoise)
    if chromaDenoise is not None:
        control.setChromaDenoise(chromaDenoise)

    # TODO: Add contrast, exposure compensation, brightness, manual exposure, and saturation


def parseUserArgs(options: Dict[str, Any], cam: dai.node.ColorCamera):
    setControl(cam.initialControl,
               options.get('manualFocus', None),
               options.get('afMode', None),
               options.get('awbMode', None),
               options.get('sceneMode', None),
               options.get('antiBandingMode', None),
               options.get('effectMode', None),
               options.get('sharpness', None),
               options.get('lumaDenoise', None),
               options.get('chromaDenoise', None),
            )


class CameraComponent(Component):
    # Users should have access to these nodes
    camera: Union[dai.node.ColorCamera, dai.node.MonoCamera] = None
    encoder: dai.node.VideoEncoder = None
    _replay: Optional[Replay] = None # Replay module

    out: dai.Node.Output = None

    def __init__(self,
                 pipeline: dai.Pipeline,
                 source: str,
                 resolution: Union[None, str, dai.ColorCameraProperties.SensorResolution, dai.MonoCameraProperties.SensorResolution] = None,
                 fps: Optional[float] = None,
                 name: Optional[str] = None,
                 out: Union[None, bool, str] = None,
                 encode: Union[None, str, bool, dai.VideoEncoderProperties.Profile] = None,
                 control: bool = False,
                 replay: Optional[Replay] = None,
                 args: Any = None,
                 ):
        """
        Args:
            pipeline (dai.Pipeline)
            source (str): Source of the camera. Either color/rgb/right/left
            resolution: Camera resolution
            fps: Camera FPS
            name (str, optional): name of the camera
            out (bool, default False): Whether we want to stream frames to the host computer
            encode: Encode streams before sending them to the host. Either True (use default), or mjpeg/h264/h265
            control (bool, default False): control the camera from the host keyboard (via cv2.waitKey())
            replay (Replay object, optional): Replay
            args (Any, optional): Set the camera components based on user arguments
        """
        super().__init__()
        self.pipeline = pipeline

        self._replay = replay
        self._sourceName = source.lower()

        self._parseSource(source)

        if resolution and self.camera:
            from .parser import parseResolution
            self.camera.setResolution(parseResolution(resolution))

        if fps:
            if self.camera:
                self.camera.setFps(fps)
            elif self._replay:
                self._replay.setFps(fps)

        if out:
            super().createXOut(
                pipeline,
                type(self._replay) if self._replay else type(self),
                name = out,
                out = self.camera.video if self._isColor() else self.out,
                depthaiMsg = dai.ImgFrame
            )

    def _parseSource(self, source: str) -> None:
        if source.upper() == "COLOR" or source.upper() == "RGB":
            if self._replay:
                if not self._replay.color:
                    raise Exception('Color stream was not found in specified depthai-recording!')
                self.out = self._replay.color.out
            else:
                self.camera = self.pipeline.create(dai.node.ColorCamera)
                self.camera.setInterleaved(False) # Most NNs are CHW (planar)
                self.camera.setBoardSocket(dai.CameraBoardSocket.RGB)
                self.camera.setPreviewNumFramesPool(20)
                self.out = self.camera.preview

        elif source.upper() == "RIGHT" or source.upper() == "MONO":
            if self._replay is None:
                self.camera = self.pipeline.create(dai.node.MonoCamera)
                self.camera.setBoardSocket(dai.CameraBoardSocket.RIGHT)
                self.out = self.camera.out
            else:
                if not self._replay.right:
                    raise Exception('Right stream was not found in specified depthai-recording!')
                self.out = self._replay.right.out
        elif source.upper() == "LEFT":
            if self._replay is None:
                self.mono = self.pipeline.create(dai.node.MonoCamera)
                self.mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
                self.out = self.mono.out
            else:
                if not self._replay.left:
                    raise Exception('Left stream was not found in specified depthai-recording!')
                self.out = self._replay.left.out
        else:
            raise ValueError(f"Source name '{source}' not supported!")

    # Should be mono/color camera agnostic. Also call this from __init__ if args is enabled
    def configureCamera(self,
                        preview: Union[None, str, Tuple[int, int]] = None, # Set preview size
                        fps: Optional[float] = None # Set fps
                        ) -> None:
        """
        Configure resolution, scale, FPS, etc.
        """
        if fps:
            if self._replay:
                print("Setting FPS for depthai-recording isn't yet supported. This configuration attempt will be ignored.")
            else:
                self.camera.setFps(fps)

        if preview:
            from .parser import parseSize
            preview = parseSize(preview)

            if self._replay: self._replay.setResizeColor(preview)
            elif self._isColor(): self.camera.setPreviewSize(preview)
            else:
                # TODO: Use ImageManip to set mono frame size
                raise NotImplementedError("Not yet implemented")

    def configColorCamera(self,
                          interleaved: Optional[bool] = None,
                          colorOrder: Union[None, dai.ColorCameraProperties.ColorOrder, str] = None,
                          ) -> None:
        # TODO: add option for other configs
        if not self._isColor():
            print("Attempted to configure ColorCamera, but this component doesn't have it. Config attempt ignored.")
            return

        if interleaved is not None:
            self.camera.setInterleaved(interleaved)
        if colorOrder:
            if isinstance(colorOrder, str):
                colorOrder = getattr(dai.ColorCameraProperties.ColorOrder, colorOrder.upper())
            self.camera.getColorOrder(colorOrder)

    def _isColor(self) -> bool: return isinstance(self.camera, dai.node.ColorCamera)
    def _isMono(self) -> bool: return isinstance(self.camera, dai.node.MonoCamera)

    def getSize(self) -> Tuple[int, int]:
        if self._isColor(): return self.camera.getPreviewSize()
        elif self._isMono(): raise NotImplementedError()
        elif self._replay: return self._replay.getShape(self._sourceName)

    def configureEncoder(self,
                         ):
        """
        Configure quality, enable lossless,
        """
        if self.encoder is None:
            print('Video encoder was not enabled! This configuration attempt will be ignored.')
            return

        # self.encoer.

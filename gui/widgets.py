from PyQt5.QtWidgets import QSlider

from utils.logger import setup_logger

logger = setup_logger(__name__)



class SenseSlider(QSlider):
    """
    Simple QSlider wrapper for monitoring user interactions  
    """
    def __init__(self, *args, **kwargs):
        self._slider_holded = False
        super().__init__(*args, **kwargs)
        self.sliderPressed.connect(self.onSliderPressed)
        self.sliderReleased.connect(self.onSliderReleased)
        
    @property
    def slider_holded(self):
        return self._slider_holded
    
    def onSliderPressed(self):
        self._slider_holded = True
        
    def onSliderReleased(self):
        self._slider_holded = False
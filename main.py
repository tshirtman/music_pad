''' A music pad application for tablets
'''
from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from ConfigParser import SafeConfigParser
from json import JSONDecoder
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from functools import partial

JSON_DECODER = JSONDecoder().raw_decode

CONFIG = SafeConfigParser()
CONFIG.read(('.default_config.ini', 'config.ini', ))


class PlayButton(Button):
    ''' a button to play sound
    '''
    sound = StringProperty('')
    #toggle = BooleanProperty('')
    loop = BooleanProperty(False)
    fadein = NumericProperty(0)
    fadeout = NumericProperty(0)
    volume = NumericProperty(1)

    def on_sound(self, *args):
        self._sound = SoundLoader.load(self.sound)
        self._sound.loop = self.loop
        self._sound.bind(on_stop=self.state_normal)
        self._sound.bind(on_play=self.state_down)

    def on_loop(self, *args):
        self._sound.loop = self.loop

    def state_normal(self, *args):
        self.state = 'normal'

    def state_down(self, *args):
        self.state = 'down'

    def on_touch_down(self, touch, *args):
        if self.collide_point(*touch.pos):
            if not hasattr(self, '_sound') or self.state == 'down' and not self.loop:
                return

            if self.loop and self.state == 'down':
                if self.fadeout:
                    a = Animation(volume=0, d=self.fadeout)
                    a.bind(on_complete=lambda *x: self._sound.stop())
                    a.start(self._sound)
                else:
                    self._sound.stop()

            elif self.fadein:
                self._sound.volume = 0
                a = Animation(volume=self.volume, d=self.fadein)
                a.start(self._sound)
                self._sound.play()

                if self.fadeout:
                    a = Animation(d=self._sound.length - self.fadeout) + Animation(volume=0, d=self.fadeout)
                    a.start(self._sound)

            else:
                self._sound.play()

        else:
            return super(PlayButton, self).on_touch_down(touch, *args)


    def on_touch_up(self, touch, *args):
        pass


class MusicPad(App):
    ''' see module documentation
    '''
    width = NumericProperty()
    height = NumericProperty()

    def build(self):
        root = super(MusicPad, self).build()
        self.width = int(CONFIG.get('default', 'width'))
        self.height = int(CONFIG.get('default', 'height'))
        return root

    def on_width(self, *args):
        '''
        '''
        self.root.clear_widgets()
        for i in range(self.height):
            for j in range(self.width):
                _id = '%s_%s' % (i, j)
                print _id
                c = {}

                if CONFIG.has_option('buttons', _id):
                    options = CONFIG.get('buttons', _id)
                    for k, v in JSON_DECODER(options)[0].items():
                        c[str(k)] = v

                w = PlayButton(**c)
                self.root.add_widget(w)

    def on_height(self, *args):
        '''
        '''
        self.on_width(*args)

    def on_stop(self):
        self.on_pause()

    def on_pause(self):
        with open('config.ini', 'w') as f:
            CONFIG.write(f)
        return True

    def on_resume(self):
        return True


if __name__ == '__main__':
    MusicPad().run()

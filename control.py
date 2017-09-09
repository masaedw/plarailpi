from flask import Flask
import subprocess

class MasCon:
    def __init__(self):
        self.speed = 0 # read only attribute. use set_speed() to write

        self.gpio_max = 700
        self.gpio_ina = 12
        self.gpio_inb = 13
        self.scale = 5

    """
    BD65496MUV IO truth table
    |      INPUT      |          OUTPUT           |
    | PWM | INA | INB | OUTA | OUTB | OUTPUT MODE |
    |-----|-----|-----|------|------|-------------|
    |  L  |  L  |  L  |   Z  |   Z  |    Open     |
    |  L  |  H  |  L  |   H  |   L  |   Forward   |
    |  L  |  L  |  H  |   L  |   H  |   Reverse   |
    |  L  |  H  |  H  |   L  |   L  | Short Break |
    """

    def __sh(self, args):
        subprocess.run(["echo"] + args)
        subprocess.run(args)

    def init_gpio(self):
        self.__sh(["gpio", "-g", "mode", str(self.gpio_ina), "pwm"])
        self.__sh(["gpio", "-g", "mode", str(self.gpio_inb), "pwm"])
        self.__sh(["gpio", "pwm-ms"])

    def __gpio_pwm(self, pin, value):
        self.__sh(["gpio", "-g", "pwm", str(pin), str(value)])

    def __sync_gpio(self):
        value = int(abs(self.speed) * self.gpio_max / self.scale)

        if self.speed < 0:
            self.__gpio_pwm(self.gpio_ina, 0)
            self.__gpio_pwm(self.gpio_inb, value)
        elif self.speed == 0:
            self.__gpio_pwm(self.gpio_ina, 0)
            self.__gpio_pwm(self.gpio_inb, 0)
        else:
            self.__gpio_pwm(self.gpio_inb, 0)
            self.__gpio_pwm(self.gpio_ina, value)

    def set_speed(self, s):
        if -self.scale <= s and s <= self.scale:
            self.speed = s
        self.__sync_gpio()

    def speedup(self):
        self.set_speed(self.speed + 1)

    def speeddown(self):
        self.set_speed(self.speed - 1)

app = Flask(__name__)
mascon = MasCon()

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/up")
def up():
    mascon.speedup()
    return "Hello World!"

@app.route("/down")
def down():
    mascon.speeddown()
    return "Hello World!"

if __name__ == "__main__":
    mascon.init_gpio()
    app.run(host='0.0.0.0')

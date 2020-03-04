from PyFel import SunxiFel


class SunXiFel:
    def __init__(self):
        pass

    def run(self):
        try:
            fel = SunxiFel.SunxiFel()
            fel.check()
        except FileNotFoundError as x:
            print("Error scanning USB: {}".format(x))
            return

        fel.verify()


if (__name__ == "__main__"):
    program = SunXiFel()
    program.run()

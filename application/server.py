import os
import tornado.web
from machines.machine_loader import MachineLoader
import machines.number_recognizer
from machines.number_recognizer.validator import Validator


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", title="title")


class BaseHandler(tornado.web.RequestHandler):
    MACHINE_SESSION_KEY = "number_recognizer"


class PredictionHandler(BaseHandler):

    def post(self):
        resp = {"result": str(-1)}
        data = self.get_arguments("data[]")
        new_number = self.get_arguments("new_number")
        #print(new_number)

        validated = Validator.validate_data(data)
        machine = MachineLoader.load(machines.number_recognizer)
        if len(validated) > 0:
            predicted = machine.predict(validated)
            #print(validated)
            import numpy as np
            import scipy
            #scipy.mise.toimage(np.array(validated).reshape(8,8), cmin=0.0, cmax=16).save('outfile.jpg')
            resp["result"] = str(int(predicted[0]))

            with open('D:/number_recognizer/test.txt','a') as thefile:
                for item in validated:
                    thefile.write("%s\t" % item)
                thefile.write("\n")


            #from random import randint
            #b = randint(0,9)
            #print('please input the number: %d' % b)
            with open('D:/number_recognizer/target.txt','a') as thefile:
                thefile.write("%s\n" % new_number[0])


        self.write(resp)


class FeedbackHandler(BaseHandler):

    def post(self):
        data = self.get_arguments("data[]")
        result = ""

        feedback = Validator.validate_feedback(data)
        if len(feedback) > 0:
            # save feedback to file
            MachineLoader.feedback(machines.number_recognizer, feedback)

            # online training
            machine = MachineLoader.load(machines.number_recognizer)
            machine.partial_fit(feedback[1:], [feedback[0]])
            MachineLoader.save(machines.number_recognizer, machine)
        else:
            result = "feedback format is wrong."

        resp = {"result": result}
        self.write(resp)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/predict", PredictionHandler),
            (r"/feedback", FeedbackHandler),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=os.environ.get("SECRET_TOKEN", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
            xsrf_cookies=True,
            debug=True,
        )

        super(Application, self).__init__(handlers, **settings)

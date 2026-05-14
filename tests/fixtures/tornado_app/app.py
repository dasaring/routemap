import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'message': 'Hello, world'})


class UsersHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'users': []})

    def post(self):
        self.write({'created': True})


class UserHandler(tornado.web.RequestHandler):
    def get(self, user_id):
        self.write({'user_id': user_id})

    def put(self, user_id):
        self.write({'updated': user_id})

    def delete(self, user_id):
        self.write({'deleted': user_id})


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/users', UsersHandler),
        (r'/users/([0-9]+)', UserHandler),
    ])


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

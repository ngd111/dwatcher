from flask import Flask, abort, jsonify, make_response
from flask_restful import Resource, Api
#import sqlite3
import pymysql

app = Flask(__name__)
api = Api(app)


class ReadFilePath(Resource):
    def __init__(self):
	self.conn = pymysql.connect(host='localhost', port=3306, user='recuser', password='ghansol111@', db='recording',charset='utf8', autocommit=False)

    def __del__(self):
        self.conn.close()

    def get(self, calluuid):
        query = 'select filepath from recording where calluuid = %s'
        rv = self._query_db(query, calluuid)
        return {calluuid: rv}

    #def _query_db(query, args=(), one=True):
    def _query_db(self, query, _calluuid):
        #query_del = 'delete from recording where calluuid = ?'
        rv = []
        resultcnt = 0
        try:
            cur = self.conn.cursor()
            resultcnt = cur.execute(query, (_calluuid, ))
            r = cur.fetchone()
            if resultcnt > 0:
               rv.append(r)
            cur.close()
        except Exception, e:
            #self.logger.write_log("critical", ("config file open error => {0}:".format(e)))
            print('!!error : {0}:'.format(e))
            pass

        if resultcnt == 0:
            abort(404)

        return rv[0]
        #return (rv[0] if rv else None) if one else rv

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin','*')
        return response

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error':'Not found'}), 404)

@app.route('/')
def base_route_point():
    return "Welcome to the Recording file search service"

api.add_resource(ReadFilePath, '/recording/<string:calluuid>')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)

# -*- python -*-
# author: krozin@gmail.com
# db: created 2016/10/30.
# copyright

import datetime
import hashlib
import json
import os
import random
import unittest

from sqlalchemy import Column, Boolean, Integer, String, DateTime, Binary
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import DBPATH

Base = declarative_base()


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    barcode = Column(String(10))
    date_time = Column(DateTime)
    status = Column(Boolean)
    result = Column(Binary)

    def __init__(self,
                 barcode='ba',
                 d=datetime.datetime.now(),
                 status=False,
                 result=json.dumps({'aim': 'na',
                                    'precondition': 'pa',
                                    'actions': ['do step1', 'do step2'],
                                    'expected': ['something1', 'something2']
                                     })):
        self.barcode = barcode
        self.date_time = d
        self.status = status
        self.result = json.dumps(result)

    def __repr__(self):
        return "<Result({0} {1}{2}{3} {4})>".format(
            self.id,
            self.barcode,
            self.date_time,
            self.status,
            self.result)


class DbProxy(object):

    def __init__(self):
        if not os.path.exists(DBPATH):
            with open(DBPATH, 'a'):
                os.utime(DBPATH, None)

        self._init_engine(uri='sqlite:///{}'.format(DBPATH), echo=True)
        self._init_db()

    def _init_engine(self, uri, **kwards):
        self.engine = create_engine(uri, **kwards)

    def _init_db(self):
        self.session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)

    def add_result(self, **kwargs):
        res = Result(barcode=kwargs.get('barcode'),
                     status=kwargs.get('status'),
                     result=kwargs.get('result'),
                     d=datetime.datetime.now())
        self.session.add(res)
        self.session.commit()
        return res.id

    def get_all(self, limit=-1, order1=Result.date_time):
        return (self.session.query(Result).order_by(desc(order1))
                .limit(limit).all())

    def is_barcode_present(self, barcode):
        present = self.session.query(Result).filter_by(barcode=str(barcode)).first() is not None
        return present

    def get_report_by_date(self, date):
        record = self.session.query(Result).filter_by(date_time=str(date)).first()
        return record.result

    def delete_record_by_barcode(self, barcode):
        self.session.query(Result).filter_by(barcode=str(barcode)).delete()
        self.session.commit()

    def close_session(self):
            self.session.commit()
            self.session.close()


class TestBDProxy(unittest.TestCase):
    def test_write_read(self):
        dbproxy = DbProxy()
        barcode = hashlib.sha256(os.urandom(30).encode('base64')[:-1]).hexdigest()[:10]
        dbproxy.add_result(barcode=barcode,
                           status=random.choice([False, True]),
                           result=random.choice([{'TP1': True}, {'TP2': True}, {'NA': True}]))
        res = any(i.barcode == barcode for i in dbproxy.get_all())
        self.assertTrue(res, "Something wrong")

if __name__ == '__main__':
    unittest.main(verbosity=7)

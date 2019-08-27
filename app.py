import datetime, json, re, numpy as np, simplejson, time
from collections import defaultdict
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import Mutable
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from decimal import *
# Init app
app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yandex:apidbpassword@localhost/api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)


# Check a non-empty string containing at least one letter or number, no more than 256
def noEmpty(field):
    return re.search(r'^[\w\d]+', field) and (0 < len(str(field)) < 257)


# Check "appartment" field
def checkAparment(rs):
    try:
        if rs.__contains__('appartement') and rs['appartement'] > 0 and type(rs['appartement']) == int:
            return rs['appartement']
        elif rs.__contains__('apartment') and rs['apartment'] > 0 and type(rs['apartment']) == int:
            return rs['apartment']
        else:
            return False
    except:
        return False


# Check Date format and validated
def checkDate(date_string):
    try:
        match = re.fullmatch(r'\d\d\.\d\d\.\d{4}', date_string)
        if match:
            bDate = datetime.datetime.strptime(date_string, '%d.%m.%Y')
            nDate = datetime.datetime.utcnow()
            if bDate < nDate:
                return bDate.date()
            else:
                return False
        else:
            return False
    except:
        return False


# Check relatives
def checkRelatives(rlt_dict):
    if len(rlt_dict) == 0: return True
    for key, val in rlt_dict.items():
        for i in val:
            if (key == i or rlt_dict.__contains__(i) == False or key not in rlt_dict[i]):
                return False
            rlt_dict[i].remove(key)
    return True


# Check fields from POST/PATCH/GET
def checkFields(field):
    fields = ['town', 'street', 'building', 'apartment',
              'appartement', 'name', 'birth_date', 'gender', 'relatives']
    for key in field:
        if key not in fields:
            return False
    return True


# Check key
def checkKey(rs, key):
    if rs.__contains__(key):
        return True
    return False


# Calculate age
def get_age(b_day):
    utc_n = datetime.datetime.utcnow()
    return utc_n.year - b_day.year - ((utc_n.month, utc_n.day) < (b_day.month, b_day.day))

# Timeout Checker
def time_out(counter, limit=10000, timeout=10):
    counter += 1
    if counter > limit:
        time.sleep(timeout)
        counter = 0
    return counter

# Class Mutable
class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


# Import Class/Model
class Import(db.Model):
    import_id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    citizens = db.relationship('Citizen', backref='_import_id')


# Import Schema
class ImportSchema(ma.Schema):
    class Meta:
        fields = ('import_id',)


# Citizen Class/Model
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.Integer, db.ForeignKey('import.import_id'))
    citizen_id = db.Column(db.Integer, nullable=False)
    town = db.Column(db.VARCHAR(256), nullable=False)
    street = db.Column(db.VARCHAR(256), nullable=False)
    building = db.Column(db.VARCHAR(256), nullable=False)
    apartment = db.Column(db.Integer, nullable=False)
    name = db.Column(db.VARCHAR(256), nullable=False)
    birth_date = db.Column(db.DATE, nullable=False)
    gender = db.Column(db.VARCHAR(6), nullable=False)
    relatives = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)))


# Citizen Schema
class CitizenSchema(ma.Schema):
    class Meta:
        fields = ('citizen_id', 'town', 'street', 'building', 'apartment', 'name', 'birth_date', 'gender', 'relatives')


# Init Schema
import_schema = ImportSchema()
citizen_schema = CitizenSchema()
citizens_schema = CitizenSchema(many=True)


# Create a Import/Citizen
@app.route('/imports', methods=['POST'])
def add_imports():
    try:
        new_import = Import()
        db.session.add(new_import)
        relatives_dict = {}
        cit_id, counter = [], 0
        for rs in request.json['citizens']:
            rs['apartment'] = checkAparment(rs)
            if (len(rs) == 9 and (rs['citizen_id'] > 0 and type(rs['citizen_id']) == int) and noEmpty(rs['town'])
                    and noEmpty(rs['street']) and noEmpty(rs['building'])
                    and rs['apartment'] and (
                            re.fullmatch(r'^[\D]+', rs['name'].strip()) and (0 < len(rs['name']) < 257))
                    and (re.fullmatch(r'^female|male', rs['gender']))
                    and (rs['relatives'] == [] or len(rs['relatives']) > 0)
                    and (len(set(rs['relatives'])) == len(list(rs['relatives'])))
                    and rs['citizen_id'] not in cit_id):

                if len(rs['relatives']) > 0: relatives_dict[rs['citizen_id']] = rs['relatives']

                db.session.add(Citizen(_import_id=new_import, citizen_id=rs['citizen_id'], town=rs['town'],
                                       street=rs['street'], building=rs['building'], apartment=rs['apartment'],
                                       name=rs['name'], birth_date=checkDate(rs['birth_date']), gender=rs['gender'],
                                       relatives=rs['relatives']))
                cit_id.append(rs['citizen_id'])
                counter = time_out(counter)
            else:
                return {}, 400

        del cit_id  # delete citizen_id list

        if checkRelatives(relatives_dict):
            db.session.commit()
            return jsonify(data=import_schema.dump(new_import)), 201
        else:
            return {}, 400

    except:
        return {}, 400


# PATCH - modified information about the specified dataset
@app.route('/imports/<import_id>/citizens/<citizen_id>', methods=['PATCH'])
def update_citizen(import_id, citizen_id):
    try:
        rj = request.json
        if len(rj) > 0 and checkFields(rj):
            citizen = Citizen.query.filter_by(import_id=import_id, citizen_id=citizen_id).first()
            if citizen is None: return {}, 404
            checkS = True
            if checkS and checkKey(rj, 'town'):
                if noEmpty(rj['town']):
                    citizen.town = rj['town']
                else:
                    checkS = False

            if checkS and checkKey(rj, 'street'):
                if noEmpty(rj['street']):
                    citizen.street = rj['street']
                else:
                    checkS = False

            if checkS and checkKey(rj, 'building'):
                if noEmpty(rj['building']):
                    citizen.building = rj['building']
                else:
                    checkS = False

            if checkS and (checkKey(rj, 'appartement') or checkKey(rj, 'apartment')):
                apart = checkAparment(rj)
                if apart:
                    citizen.apartment = apart
                else:
                    checkS = False

            if checkS and checkKey(rj, 'name'):
                if re.fullmatch(r'^[\D]+', rj['name'].strip()) and (0 < len(rj['name']) < 257):
                    citizen.name = rj['name']
                else:
                    checkS = False

            if checkS and checkKey(rj, 'birth_date'):
                birth_date = checkDate(rj['birth_date'])
                if bool(birth_date):
                    citizen.birth_date = birth_date
                else:
                    checkS = False

            if checkS and checkKey(rj, 'gender'):
                if re.fullmatch(r'^female|male', rj['gender']):
                    citizen.gender = rj['gender']
                else:
                    checkS = False

            if checkS and checkKey(rj, 'relatives'):
                if ((rj['relatives'] == [] or len(rj['relatives']) > 0)
                        and len(set(rj['relatives'])) == len(rj['relatives'])
                        and (citizen.citizen_id not in list(rj['relatives']))
                ):
                    if rj['relatives'] != list(citizen.relatives):
                        if rj['relatives'] == '[]':
                            # remove citizen.citizen_id from relatives
                            for v in citizen.relatives:
                                cUpdt = Citizen.query.filter_by(import_id=import_id, citizen_id=v).first()
                                l = list(cUpdt.relatives)
                                l.remove(citizen.citizen_id)
                                cUpdt.relatives = l
                            # change citizen.relatives
                            citizen.relatives = rj['relatives']
                        else:
                            # remove citizen.citizen_id from relatives
                            for v in citizen.relatives:
                                cUpdt = Citizen.query.filter_by(import_id=import_id, citizen_id=v).first()
                                if cUpdt.citizen_id not in rj['relatives']:
                                    l = list(cUpdt.relatives)
                                    l.remove(citizen.citizen_id)
                                    cUpdt.relatives = l

                            # add citizen.citizen_id to relatives
                            for v in rj['relatives']:
                                cUpdt = Citizen.query.filter_by(import_id=import_id, citizen_id=v).first()
                                l = list(cUpdt.relatives)
                                if citizen.citizen_id not in l:
                                    l.append(citizen.citizen_id)
                                    cUpdt.relatives = l

                            # change citizen.relatives
                            citizen.relatives = rj['relatives']

                else:
                    checkS = False

            if checkS:
                db.session.commit()
                citizen.relatives = [int(i) for i in citizen.relatives]
                citizen.birth_date = citizen.birth_date.strftime('%d.%m.%Y')
                citizen.gender = citizen.gender.strip()
                return jsonify(data=citizen_schema.dump(citizen)), 200
            else:
                return {}, 400
        else:
            return {}, 400
    except:
        return {}, 400


# GET - returns a list of all residents for the specified dataset
@app.route('/imports/<import_id>/citizens', methods=['GET'])
def get_citizen(import_id):
    try:
        all_citizens = Citizen.query.filter_by(import_id=import_id).all()
        if all_citizens:
            counter = 0
            result = []
            for row in all_citizens:
                result.append(dict(citizen_id=row.citizen_id, town=row.town, street=row.street, building=row.building,
                     apartment=row.apartment, name=row.name, birth_date=row.birth_date.strftime('%d.%m.%Y'),
                     gender=row.gender.strip(), relatives=[int(i) for i in row.relatives]))
                counter = time_out(counter)
            return jsonify(data=result), 200
        return {}, 404
    except:
        return {}, 400


# GET - /imports/$import_id/citizens/birthdays
@app.route('/imports/<import_id>/citizens/birthdays')
def get_birthdays(import_id):
    try:
        sql = "SELECT citizen_id AS id, date_part('month', birth_date) AS m_int, relatives " \
              "FROM citizen WHERE import_id = %d AND array_length(relatives, 1) > 0;" % int(import_id)
        result = db.session.execute(sql)

        rs, cnt = {}, {}
        counter = 0
        for row in result:
            rs[row["id"]] = [[int(i) for i in row["relatives"]], int(row["m_int"])]
            cnt[row["id"]] = [0 for i in range(12)]
            counter = time_out(counter)

        if (len(rs)):
            del result
            for k, v in rs.items():
                for i in v[0]:
                    cnt[k][rs[i][1] - 1] += 1
                    cnt[i][v[1] - 1] += 1
                    rs[i][0].remove(k)
                    rs[k][0].remove(i)
            d_moth = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [],
                      7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
            for k, v in cnt.items():
                for i in range(12):
                    if v[i] > 0:
                        d_moth[i + 1].append({"citizen_id": k, "presents": v[i]})
            return jsonify(data=d_moth), 200

        return {}, 404

    except:
        return {}, 400


# GET - /imports/$import_id/towns/stat/percentile/age
@app.route('/imports/<import_id>/towns/stat/percentile/age')
def get_percentile(import_id):
    try:
        sql = "SELECT town, birth_date FROM citizen WHERE import_id = %d;" % int(import_id)
        result = db.session.execute(sql)
        rs = defaultdict(list)
        counter = 0
        for row in result:
            rs[row['town']].append(get_age(row['birth_date']))
            counter = time_out(counter)

        if len(rs):
            percentile_town = []  # percentile by town
            for t, al in rs.items():
                current_dict = {'town': t}
                for i in [50, 75, 99]:
                    current_dict[f'p{i}'] = float("%0.2f" % (np.percentile(al, i, interpolation='linear')))
                percentile_town.append(current_dict)
            return jsonify(data=percentile_town), 200

        return {}, 404
    except:
        return {}, 400

# Run Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

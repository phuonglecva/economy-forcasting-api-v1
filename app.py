from flask import Flask
from flask.json import jsonify
from flask_restful import Api, Resource
from data_loader import read_cpi, read_iip, get_cpi_timeline, get_unemployment_rate, get_revenue_expenditure, load_gdp, load_xnk
from flask_cors import CORS
from model.data_loader import *
from flask import request
from datetime import datetime

app = Flask(__name__)
api = Api(app)
cors = CORS(app)


@app.route('/api/v1/<city>/cpies')
def get_cpi(city):
    cpi_data = read_cpi(city)
    timeline = get_cpi_timeline(city)
    return {
        'data': {
            'timeline': timeline,
            'cpi': cpi_data
        }
    }


@app.route('/api/v1/<city>/cpies/<int:num_month>')
def get_cpi_by_num_month(city, num_month):
    reverse = request.args.get('reverse', None) in ['True', 'true', 't', 1]
    cpi_data = read_cpi(city)
    timeline = get_cpi_timeline(city)
    return {
        'params': reverse,
        'data': {
            'timeline': timeline[-num_month:][::-1] if reverse else timeline[-num_month:],
            'cpi': [
                {'name': row['name'],
                 'val': row['val'][-num_month:][::-1] if reverse else row['val'][-num_month:]

                 } for row in cpi_data
            ]
        }
    }

# @app.route('/api/v1/<city>/cpies/<int:id>')
# def get_cpi_by_id(city, id):
#     cpi_data = read_cpi(city)
#     timeline = get_cpi_timeline(city)
#     print(cpi_data)
#     return {
#         'data': {
#             'timeline': timeline,
#             'sub': cpi_data[id]
#         }
#     }


@app.route('/api/v1/<city>/iips')
def get_iip(city):
    values, index, timeline = read_iip(city)
    return {
        'data':  {
            'timeline': timeline,
            'iip': values[0],
            'subs': [
                {'name': name, 'value': val} for name, val in zip(index[1:], values[1:])
            ]
        }
    }


@app.route('/api/v1/<city>/iips/<int:num_month>')
def get_iip_by_num_month(city, num_month):
    reverse = request.args.get('reverse', None) in ['True', 'true', 't', 1]
    values, index, timeline = read_iip(city)
    return {
        'data':  {
            'timeline': timeline[-num_month:][::-1] if reverse else timeline[-num_month:],
            'iip': values[0][-num_month:][::-1] if reverse else values[0][-num_month:],
            'subs': [
                {'name': name,
                 'value': val[-num_month:][::-1] if reverse else val[-num_month:]} for name, val in zip(index[1:], values[1:])
            ]
        }
    }


# @app.route('/api/v1/<city>/iips/<int:pk>')
# def get_iip_by_id(city, pk):
#     values, index, timeline = read_iip(city)
#     return {
#         'data':  {
#             'timeline': timeline,
#             'subs': [
#                 {'name': index[pk], 'value': values[pk]}
#             ]
#         }
#     }


@app.route('/api/v1/<city>/cpies/forecast/<int:next>')
def forecast_cpi(city, next):
    forecasts = load_forecast()
    index_names = get_cpi_name()
    timeline = get_cpi_timeline(city)
    return {
        'data': {
            'forecasts': {
                'cpi': forecasts['cpi'][:next],
                'subs': [{'name': name, 'val': sub[:next]} for name, sub in zip(index_names[1:], forecasts['subs'])],
                'from_time': timeline[-3]
            }
        }
    }


@app.route('/api/v1/<city>/unemployment', strict_slashes=False)
def get_unemployment(city):
    timeline, _, data = get_unemployment_rate(None, False, city)
    return {
        'data': {
            'unemployment': data,
            'timeline': timeline
        }
    }

@app.route('/api/v1/<city>/unemployment/<int:nm>')
def get_unemployment_by_nm(city, nm):
    reverse = request.args.get('reverse', None) in ['True', 'true', 't', 1]

    timeline, _, data = get_unemployment_rate(nm, reverse, city)
    return {
        'data': {
            'unemployment': data,
            'timeline': timeline
        }
    }


@app.route('/api/v1/<city>/thuchi', strict_slashes=False)
def get_thuchi(city):
    data, timeline = get_revenue_expenditure(None, False, city)
    return jsonify({
        'data': {
            'thuchi_data': data,
            'timeline': timeline
        }
    })

@app.route('/api/v1/<city>/thuchi/<int:nm>')
def get_thuchi_by_nm(city, nm):
    reverse = request.args.get('reverse', None) in ['True', 'true', 't', 1]
    print(reverse, nm)
    data, timeline = get_revenue_expenditure(nm, reverse, city)
    return jsonify({
        'data': {
            'thuchi_data': data,
            'timeline': timeline
        }
    })


@app.route('/api/v1/<city>/gdps')
def get_gdp(city):
    data = load_gdp(city)
    return jsonify({
        'data': data
    })


@app.route('/api/v1/<city>/gdps/<int:nm>')
def get_gdp_by_nm(city, nm):
    reverse = request.args.get('reverse', None) in ['True', 'true', 't', 1]
    data = load_gdp(city)

    return jsonify({
        'data': {
            'year': data['year'][-nm:][::-1] if reverse else data['year'][-nm:],
            'values': data['values'][-nm:][::-1] if reverse else data['values'][-nm:],
            'rates': data['rates'][-nm:][::-1] if reverse else data['rates'][-nm:],
            'value_unit': 'ty dong'
        }
    })


@app.route('/api/v1/<city>/xnk')
def get_xnk(city):
    xk_val, xk, nk_val, nk, years = load_xnk(city)
    names = ['Kim ngạch tháng hiện tại', 'Tính chung từ đầu năm', 'Kinh tế nhà nước',
             'Kinh tế ngoài nhà nước',
             'Kinh tế có vốn đầu tư nước ngoài', ]
    xk_array = np.array(xk, dtype='float').T
    xk_array[np.isnan(xk_array)] = 0
    nk_array = np.array(nk, dtype='float').T
    nk_array[np.isnan(nk_array)] = 0

    xk_val = np.array(xk_val, dtype='float').T
    xk_val[np.isnan(xk_val)] = 0
    nk_val = np.array(nk_val, dtype='float').T
    nk_val[np.isnan(nk_val)] = 0
    years = [year[:-4] + '-' + year[-4:] for year in list(years)]
    return jsonify({
        'data': {
            'xuatkhau': [{'name': name, 'val': val, 'rate': rate} for name, val, rate in zip(names, xk_val.tolist(), xk_array.tolist())],
            'nhapkhau': [{'name': name, 'val': val, 'rate': rate} for name, val, rate in zip(names, nk_val.tolist(), nk_array.tolist())],
            'years': years
        }
    })


@app.route('/api/v1/<city>/xnk/<int:num_month>')
def get_xnk_by_num_month(city, num_month):
    reverse = request.args.get('reverse', None) in ['True', 'true', 't', 1]
    xk_val, xk, nk_val, nk, years = load_xnk(city)
    names = ['Kim ngạch tháng hiện tại', 'Tính chung từ đầu năm', 'Kinh tế nhà nước',
             'Kinh tế ngoài nhà nước',
             'Kinh tế có vốn đầu tư nước ngoài', ]
    xk_array = np.array(xk, dtype='float').T
    xk_array[np.isnan(xk_array)] = 0
    nk_array = np.array(nk, dtype='float').T
    nk_array[np.isnan(nk_array)] = 0

    xk_val = np.array(xk_val, dtype='float').T
    xk_val[np.isnan(xk_val)] = 0
    nk_val = np.array(nk_val, dtype='float').T
    nk_val[np.isnan(nk_val)] = 0
    years = [year[:-4] + '-' + year[-4:] for year in list(years)]
    return jsonify({
        'data': {
            'xuatkhau': [{'name': name,
                          'val': val[:num_month][::-1] if reverse else val[:num_month],
                          'rate': rate[:num_month][::-1] if reverse else rate[:num_month]} for name, val, rate in zip(names, xk_val.tolist(), xk_array.tolist())],
            'nhapkhau': [{'name': name,
                          'val': val[:num_month][::-1] if reverse else val[:num_month],
                          'rate': rate[:num_month][::-1] if reverse else rate[:num_month]} for name, val, rate in zip(names, nk_val.tolist(), nk_array.tolist())],
            'years': years[:num_month][::-1] if reverse else years[:num_month]
        }
    })


@app.errorhandler(404)
def handler_404_err(err):
    return jsonify({
        'type': '404',
        'message': 'api not found, please check again',
    })


if __name__ == '__main__':
    app.run(debug=True)

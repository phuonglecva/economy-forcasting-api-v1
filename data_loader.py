import pandas as pd
import numpy as np
from config import variables
from datetime import datetime

data_dir = variables['data_dir']

def get_cpi_name():
    name_list = ["Chỉ số giá tiêu dùng chung",
                 "Hàng ăn và dịch vụ ăn uống",
                 "Lương thực",
                 "Thực phẩm",
                 "Ăn uống ngoài gia đình",
                 "Đồ uống và thuốc lá",
                 "May mặc, mũ nón, giáy dép",
                 "Nhà ở, điện, nước, chất đốt, VLXD",
                 "Thiết bị và đồ dùng gia đình",
                 "Thuốc và dịch vụ y tế",
                 "Giao thông",
                 "Bưu chính viễn thông",
                 "Giáo dục",
                 "Văn hóa, giải trí và du lịch",
                 "Hàng hóa và dịch vụ khác"]
    return name_list


def read_cpi(city, filename='/cpi_data.csv'):
    df = pd.read_csv('%s%s/%s' % (data_dir, city, filename), header=None)
    list_index_name = get_cpi_name()
    data = df.values.tolist()
    return [{'name': name, 'val': val} for name, val in zip(list_index_name, data)]


def read_iip(city, filename='iip_data.xlsx'):
    df = pd.read_excel('%s%s/%s' %(data_dir, city, filename))
    index_list = df.iloc[:, 0]
    columns = df.columns[1:].tolist()
    columns = [t.strftime('%Y-%m') for t in columns]
    values = df.values[:, 1:]
    return values.tolist(), index_list.tolist(), columns


def get_cpi_timeline(city, filename='cpi_timeline.xlsx'):
    df = pd.read_excel('%s%s/%s' %(data_dir, city, filename))
    list_timeline = df.columns.tolist()
    list_timeline = [t.strftime('%Y-%m') for t in list_timeline]
    return list_timeline


def get_unemployment_rate(nm, reverse, city, filename='thatnghiep.xlsx'):

    df = pd.read_excel('%s%s/%s' %(data_dir, city, filename))
    data = df.iloc[2:, :]
    time = data.iloc[:, 0].values
    values = data.iloc[:, 1:].values
    cat = ['Tỷ lệ thất nghiệp từ 15 tuổi trở lên',
           'Tỷ lệ thất nghiệp trong độ tuổi lao động']
    start_index = [0, 9]
    res = []
    regions = ['Tong so', 'Thanh thi', 'Nong thon']
    if not nm:
        nm = len(values[:, 0])
    for cat_name, start in zip(cat, start_index):
        temp_list = []
        for i, region in zip(range(start, start + 9)[0:-1:3], regions):
            temp = {}
            temp['chung'] = values[:, i].tolist()[-nm:][::-1] if reverse else values[:, i].tolist()[-nm:]
            temp['nam'] = values[:, i + 1].tolist()[-nm:][::-1] if reverse else values[:, i + 1].tolist()[-nm:]
            temp['nu'] = values[:, i + 2].tolist()[-nm:][::-1] if reverse else values[:, i + 2].tolist()[-nm:]
            temp_list.append({
                'region': region,
                'value': temp
            })
        res.append({
            'index_name': cat_name,
            'value': temp_list
        })
    years = [int(t) for t in time]
    return years[-nm:][::-1] if reverse else years[-nm:], values, res

def get_revenue_expenditure(nm, reverse, city, filename='thuchingansach.xlsx'):
    df = pd.read_excel('%s%s/%s' %(data_dir, city, filename))
    df.fillna(0,inplace=True)
    data = df.values[1:, :]
    timeline = data[:, 0]
    values = np.nan_to_num(data[:, 1:], nan=0)
    cat = ['Thu ngan sach', 'Chi ngan sach']
    sub_cat = [['Tổng thu (tỷ đồng)',	'Thu nội địa (tỷ đồng)',	'Thu lĩnh vực XNK( tỷ đồng)'],
               ['Tổng chi (tỷ đồng)', '	Chi đầu tư phát triển (tỷ đồng)	',
                'Chi thường xuyên']
               ]
    cat_start_id = [0, 9]
    res = []
    for cat_name, start_id, sub_cat_names in zip(cat, cat_start_id, sub_cat):
        # temp = {}
        temp = []
        for sub_cat_name, id in zip(sub_cat_names, range(start_id, start_id + 9)[0:-1:3]):
            temp_val = np.nan_to_num(values[:, id]).tolist()
            temp.append({
                'cat_name': sub_cat_name.strip(),
                'value': temp_val[:nm][::-1] if reverse else temp_val[:nm]
            })
            # temp[sub_cat_name.strip()] = np.nan_to_num(values[:, id]).tolist()
        res.append({
            'index_name': cat_name.strip(),
            'value': temp
        })
        # res[cat_name.strip()] = temp
    years = (pd.to_datetime(timeline).strftime('%m-%Y').values.tolist())
    return res, years[:nm][::-1] if reverse else years[:nm]
    # return  res, timeline.tolist()

def load_gdp(city, filename='gdp.xlsx'):
    data = pd.read_excel('%s%s/%s' %(data_dir, city, filename))
    year, values, rates = data.values[1:,0], data.values[1:, 1], data.values[1:, 2]
    values = [float(str(val)
                    .replace('.', '?')
                    .replace(',', '.')
                    .replace('?', ''))
              for val in values
              ]
    rates = [float(str(r).replace(',', '.')) for r in rates]
    return {
        'year': year.tolist(),
        'values': values,
        'rates': rates,
        'value_unit': 'ty dong'
    }

def load_xnk(city, filename='xnk.xlsx'):
    years = pd.read_excel('%s%s/%s' %(data_dir, city, filename), None).keys()
    data_list = [pd.read_excel('%s%s/%s' %(data_dir, city, filename), sheet_name=year, header=None) for  year in years]
    xnk_names = ['Xuất khẩu', 'Nhập khẩu']
    xuatkhau_start_id = [data.index[data.values[:, 0] == xnk_names[0]].tolist()[0] for data in data_list]
    nhapkhau_start_id = [data.index[data.values[:, 0] == xnk_names[1]].tolist()[0] for data in data_list]
    xk_data = []
    nk_data = []
    for data, start_id in zip(data_list, xuatkhau_start_id):
        xk_data.append(data.iloc[list(range(start_id, start_id + 7)), [2, 4]].values[-5:, :].T.tolist())
    for data, start_id in zip(data_list, nhapkhau_start_id):
        nk_data.append(data.iloc[list(range(start_id, start_id + 6)), [2, 4]].values[-5:, :].T.tolist())
    
    xk_data_value  = [[str(x).replace('.', '').replace(',', '.') for x in xk[0]] for xk in xk_data]
    xk_data_rate  = [[str(x).replace('%', '').replace(',','.').replace(';','').strip() for x in xk[1]] for xk in xk_data]
    nk_data_value  = [[str(x).replace('.', '').replace(',', '.') for x in xk[0]] for xk in nk_data]
    nk_data_rate  = [[str(x).replace('%', '').replace(',','.').replace(';','').strip() for x in xk[1]] for xk in nk_data]
    
    # return xuatkhau_start_id, nhapkhau_start_id, xk_data, nk_data
    return xk_data_value, xk_data_rate, nk_data_value, nk_data_rate, years
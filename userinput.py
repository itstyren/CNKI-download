condition_value_list = {
    'a': 'SU$%=|',
    'b': 'KY',
    'c': 'TI',
    'd': 'AB',
    'e': 'FT',
    'f': 'RF',
    'g': 'CLC$=|??'
}

condition_list = {
    'a': '主题',
    'b': '关键词',
    'c': '篇名',
    'd': '摘要',
    'e': '全文',
    'f': '被引文献',
    'g': 'CLC$=|??'
}

condition_type_list = {'a': 'and', 'b': 'or', 'c': 'not'}


def get_uesr_inpt():
    '''
    处理用户所需搜索的全部条件
    '''
    search_condition()


def search_condition():
    '''
    用户输入检索条件
    '''
    print('\n')
    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
    print("|　　　　　　　　　　　　　　　　　　　　　　　　　|")
    print('|　请选择检索条件：（可多选）　　　　　　　　　　　|')
    print("|（ａ）主题　　　（ｂ）关键词　　　（ｃ）篇名　　　|")
    print("|（ｄ）摘要　　　（ｅ）全文　　　　（ｆ）被引文献　|")
    print("|（ｇ）中图分类号　　　　　　　　　　　　　　　　　|")
    print("|　　　　　　　　　　　　　　　　　　　　　　　　　|")
    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
    select_condition = input("请选择（以空格分割，如a c）：")
    select_condition = select_condition.split(' ')
    print('\n')
    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
    print('您选择的是：')
    input_check=' '
    for term in select_condition:
        input_check += condition_list.get(term) + ' | '
    print(input_check)
    print('－－－－－－－－－－－－－－－－－－－－－－－－－－')
    # 搜索字段待填充list
    condition_field_list={

    }
    # 遍历用户选择，构造搜索条件部分字段
    for index, term in enumerate(select_condition):
        condition_value=input('请输入【'+condition_list.get(term)+'】：')
        # 第一个没有可选条件
        if index!=0:
            condition_type_value = input('请输入【' + condition_list.get(term) +
                                         '】条件类型:（ａ）并且　（ｂ）或者　（ｃ）不含 ')
        condition_field_list['txt_' + str(index + 1) +
                             '_sel'] = condition_value_list.get(term)
        condition_field_list['txt_' + str(index + 1) + '_value1']=condition_value
        condition_field_list['txt_'+str(index + 1)+'_relation'] = '#CNKI_AND'
        condition_field_list['txt_' + str(index + 1) + '_special1']='='
        if index!=0:
            condition_field_list['txt_' + str(index + 1) +
                                 'logical'] = condition_type_list.get(
                                     condition_type_value)

    print(condition_field_list)
thisobj_ls_res_jt = None

if thisobj_ls_res_jt:
    if thisobj_ls_res_jt >= 80:
        print("111")
    elif 60 <= thisobj_ls_res_jt < 80:
        print("222")
    elif 30 <= thisobj_ls_res_jt < 60:
        print("333")
    elif not thisobj_ls_res_jt or thisobj_ls_res_jt == 0:
        print("444")
    else:
        print("555")
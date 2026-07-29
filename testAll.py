import tran2dto3d

# danjia_dir = r"D:\Sanwei\zuobiao\DanJia\1E2-SDJ"
# tashen_dir = r"D:\Sanwei\zuobiao\TaShen\1E2-SDJ"
# danjia_dir = r"D:\Sanwei\zuobiao\DanJia\J1"
# tashen_dir = r"D:\Sanwei\zuobiao\TaShen\J1"
# danjia_dir = r"D:\Sanwei\zuobiao\DanJia\J3"
# tashen_dir = r"D:\Sanwei\zuobiao\TaShen\J3"
# danjia_dir = r"D:\Sanwei\zuobiao\DanJia\J4"
# tashen_dir = r"D:\Sanwei\zuobiao\TaShen\J4"
# danjia_dir = r"D:\Sanwei\zuobiao\DanJia\Z1"
# tashen_dir = r"D:\Sanwei\zuobiao\TaShen\Z1"
# project_path = r"D:\Sanwei\output_path"
# savepath_ui = r"D:\Sanwei\output_path\savepath_ui"



# Mac 路径配置
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/1E2-SDJ"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/1E2-SDJ"
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/J1"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/J1"
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/J3"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/J3"
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/J4"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/J4"
danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/Z1"
tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/Z1"
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/T7833"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/T7833"
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/7837"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/7837"
# danjia_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/DanJia/781"
# tashen_dir = "/Users/bilibili/Desktop/threewei/Sanwei/zuobiao/TaShen/781"
project_path = "/Users/bilibili/Desktop/threewei/Sanwei/output_path"
savepath_ui = "/Users/bilibili/Desktop/threewei/Sanwei/output_path/savepath_ui"



# todo: 7837尖点编号ID偏移+70
# todo: Z1图纸的担架1和担架4存在问题


"""
drawing_type：图纸类型
分为五类：
1. GuLou(鼓楼型)：1E2-SDJ、J1、J3、J4、Z1
2. ShangZi(上字型)：T7833、781
3. GanZi(干字型)：7837
4. ZhiLiu(直流塔)
5. YangJiao(羊角型)  
"""


tran2dto3d.tran2dto3d( danjia_dir=danjia_dir,
        tashen_dir=tashen_dir,
        project_path=project_path,
        savepath_ui=savepath_ui,
        drawing_type ="GuLou")



# 1E2-SDJ依次输入：0  911  0.9




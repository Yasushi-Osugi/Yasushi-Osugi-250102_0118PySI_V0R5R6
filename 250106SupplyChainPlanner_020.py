#241224PySI_refactoring090_060.py
#memo

# 0. planning engineを1つにまとめる

# 1. profileの簡素化
#    1-1. cost_tableの初期定義を削除
#    1-2. lot_sizeの設定の簡素化

# 2. PSIグラフの選択表示

# 3. 長期休暇のカレンダーでの設定 => 少なくともYYYY-MM-WWで指定

# 4. 関税と需要曲線のシミュレーション機能の組み込み


# memo
# root_node_out_optのsaveとload => PSIをroot_node_out_optで描画?
# opt_pathのsaveとload => networkのred lineの描画


#Loading file: global_procurement_material.csv
#Loading file: node_cost_table_inbound.csv
#Loading file: node_cost_table_outbound.csv
#Loading file: profile_tree_inbound.csv
#Loading file: profile_tree_outbound.csv
#Loading file: S_month_data.csv



# ********************************
# library import
# ********************************
import os
import shutil
import threading

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont, Tk, Menu, ttk
from tkinter import filedialog



import mpld3
from mpld3 import plugins

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#import mpld3
#from mpld3 import plugins

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import networkx as nx

from collections import defaultdict

import csv

import math
import numpy as np


import datetime as dt
from datetime import datetime as dt_datetime, timedelta

from dateutil.relativedelta import relativedelta

import calendar

import copy
import pickle

# ****************************
# Definition start of PySI modules
# ****************************



# **********************************
# create tree
# **********************************
class Node:  # with "parent"
    def __init__(self, name):

       #print("class Node init name", name)

        self.name = name
        self.children = []
        self.parent = None

        self.depth = 0
        self.width = 0

        # month 2 ISO week 変換された元のdemand
        self.iso_week_demand = None

        # node.iso_week_demand = sales_by_iso_year
        # by year dict of ISO WEEK DEMAND

        self.psi4demand = None
        self.psi4supply = None

        self.psi4couple = None

        self.psi4accume = None

        self.plan_range = 1
        self.plan_year_st = 2025

        self.safety_stock_week = 0
        # self.safety_stock_week = 2

        # self.lv_week = []

        self.lot_size = 1  # defalt setting

        # **************************
        # for NetworkX
        # **************************
        # leadtimeとsafety_stock_weekは、ここでは同じ
        self.leadtime = 1  # defalt set  # 前提:SS=0

        # Process Capacity for NetworkX
        self.nx_demand = 1  # weekly average demand by lot

        self.nx_weight = 1  # move_cost_all_to_nodeB  ( from nodeA to nodeB )
        self.nx_capacity = 1  # lot by lot

        # print("self.capacity", self.capacity)

        self.long_vacation_weeks = []

        # evaluation
        self.decoupling_total_I = []  # total Inventory all over the plan

        # position
        self.longitude = None
        self.latitude = None

        # **************************
        # BU_SC_node_profile     business_unit_supplychain_node
        # **************************

        # @240421 機械学習のフラグはstop
        ## **************************
        ## plan_basic_parameter ***sequencing is TEMPORARY
        ## **************************
        #        self.PlanningYear           = row['plan_year']
        #        self.plan_engine            = row['plan_engine']
        #        self.reward_sw              = row['reward_sw']

        # ***************************
        # business unit identify
        # ***************************

        # @240421 多段階PSIのフラグはstop
        #        self.product_name           = row['product_name']
        #        self.SC_tree_id             = row['SC_tree_id']
        #        self.node_from              = row['node_from']
        #        self.node_to                = row['node_to']

        # ***************************
        # "lot_counts" is the bridge PSI2EVAL
        # ***************************
        self.lot_counts     = [0 for x in range(0, 53 * self.plan_range)]
        self.lot_counts_all = 0  # sum(self.lot_counts)

        # ***************************
        # settinng for cost-profit evaluation parameter
        # ***************************
        self.LT_boat = 1  # row['LT_boat']

        #@ STOP self.lot_sizeがある
        #self.LOT_SIZE = 1  # row['LOT_SIZE']


        #@241229 STOP
        #1 self.SGMC_ratio = 0.1  # row['SGMC_ratio']
        #2 self.Cash_Intrest = 0.1  # row['Cash_Intrest']
        #3 self.REVENUE_RATIO = 0.1  # row['REVENUE_RATIO']

       #print("set_plan parameter")
       #print("self.LT_boat", self.LT_boat)
       #print("self.SGMC_ratio", self.SGMC_ratio)
       #print("self.Cash_Intrest", self.Cash_Intrest)
       #print("self.LOT_SIZE", self.LOT_SIZE)
       #print("self.REVENUE_RATIO", self.REVENUE_RATIO)



        # **************************
        # product_cost_profile
        # **************************


        #@241229 STOP
        #4 self.PO_Mng_cost = 1  # row['PO_Mng_cost']
        #5 self.Purchase_cost = 1  # row['Purchase_cost']
        #6 self.WH_COST_RATIO = 0.1  # row['WH_COST_RATIO']
        #* self.weeks_year = 53 * 5  # row['weeks_year']
        #7 self.WH_COST_RATIO_aWeek = 0.1  # row['WH_COST_RATIO_aWeek']


        # print("product_cost_profile parameter")
        # print("self.PO_Mng_cost", self.PO_Mng_cost)
        # print("self.Purchase_cost", self.Purchase_cost)
        # print("self.WH_COST_RATIO", self.WH_COST_RATIO)
        # print("self.weeks_year", self.weeks_year)
        # print("self.WH_COST_RATIO_aWeek", self.WH_COST_RATIO_aWeek)



        #@STOP OLD cost eval
        #@241231 STOP Refrain from "detailed lot definitions"
        ## **************************
        ## distribution_condition
        ## **************************
        #self.Indivisual_Packing = 1  # row['Indivisual_Packing']
        #self.Packing_Lot = 1  # row['Packing_Lot']
        #self.Transport_Lot = 1  # row['Transport_Lot']   #@240711 40ft単位輸送
        #self.planning_lot_size = 1  # row['planning_lot_size']
        #
        #self.Distriburion_Cost = 1  # row['Distriburion_Cost']


        #@241231 STAY
        # **************************
        # distribution_condition
        # **************************
        self.SS_days = 7  # row['SS_days']


        # print("distribution_condition parameter")
        # print("self.Indivisual_Packing", self.Indivisual_Packing)
        # print("self.Packing_Lot", self.Packing_Lot)
        # print("self.Transport_Lot", self.Transport_Lot)
        # print("self.planning_lot_size", self.planning_lot_size)
        # print("self.Distriburion_Cost", self.Distriburion_Cost)
        # print("self.SS_days", self.SS_days)

        # **************************
        # TAX_currency_condition
        # **************************
        self.HS_code = ""
        self.customs_tariff_rate = 0

        self.tariff_on_price = 0

        self.price_elasticity = 0

        # print("self.HS_code", self.HS_code)
        # print("self.customs_tariff_rate", self.customs_tariff_rate)

        # ******************************
        # evaluation data initialise rewardsを計算の初期化
        # ******************************

        # ******************************
        # Profit_Ratio #float
        # ******************************
        self.eval_profit_ratio = Profit_Ratio = 0.6

        # Revenue, Profit and Costs
        self.eval_revenue = 0
        self.eval_profit = 0

        self.eval_PO_cost = 0
        self.eval_P_cost = 0
        self.eval_WH_cost = 0
        self.eval_SGMC = 0
        self.eval_Dist_Cost = 0

        # ******************************
        # set_EVAL_cash_in_data #list for 53weeks * 5 years # 5年を想定
        # *******************************
        self.Profit = Profit = [0 for i in range(53 * self.plan_range)]
        self.Week_Intrest = Week_Intrest = [0 for i in range(53 * self.plan_range)]
        self.Cash_In = Cash_In = [0 for i in range(53 * self.plan_range)]
        self.Shipped_LOT = Shipped_LOT = [0 for i in range(53 * self.plan_range)]
        self.Shipped = Shipped = [0 for i in range(53 * self.plan_range)]

        # ******************************
        # set_EVAL_cash_out_data #list for 54 weeks
        # ******************************

        self.SGMC = SGMC = [0 for i in range(53 * self.plan_range)]
        self.PO_manage = PO_manage = [0 for i in range(53 * self.plan_range)]
        self.PO_cost = PO_cost = [0 for i in range(53 * self.plan_range)]
        self.P_unit = P_unit = [0 for i in range(53 * self.plan_range)]
        self.P_cost = P_cost = [0 for i in range(53 * self.plan_range)]

        self.I = I = [0 for i in range(53 * self.plan_range)]

        self.I_unit = I_unit = [0 for i in range(53 * self.plan_range)]
        self.WH_cost = WH_cost = [0 for i in range(53 * self.plan_range)]
        self.Dist_Cost = Dist_Cost = [0 for i in range(53 * self.plan_range)]



        # cost stracture demand
        # Price Cost Portion
        self.price_sales_shipped = 0
        self.cost_total = 0
        self.profit = 0
        self.marketing_promotion = 0
        self.sales_admin_cost = 0
        self.SGA_total = 0
        self.custom_tax = 0
        self.tax_portion = 0
        self.logistics_costs = 0
        self.warehouse_cost = 0
        self.direct_materials_costs = 0
        self.purchase_total_cost = 0
        self.prod_indirect_labor = 0
        self.prod_indirect_others = 0
        self.direct_labor_costs = 0
        self.depreciation_others = 0
        self.manufacturing_overhead = 0

        # Profit accumed root2node
        self.cs_profit_accume = 0

        # Cost Structure
        self.cs_price_sales_shipped = 0
        self.cs_cost_total = 0
        self.cs_profit = 0
        self.cs_marketing_promotion = 0
        self.cs_sales_admin_cost = 0
        self.cs_SGA_total = 0
        self.cs_custom_tax = 0
        self.cs_tax_portion = 0
        self.cs_logistics_costs = 0
        self.cs_warehouse_cost = 0
        self.cs_direct_materials_costs = 0
        self.cs_purchase_total_cost = 0
        self.cs_prod_indirect_labor = 0
        self.cs_prod_indirect_others = 0
        self.cs_direct_labor_costs = 0
        self.cs_depreciation_others = 0
        self.cs_manufacturing_overhead = 0


        # evaluated cost = Cost Structure X lot_counts
        self.eval_cs_price_sales_shipped = 0    # revenue
        self.eval_cs_cost_total = 0             # cost
        self.eval_cs_profit = 0                 # profit
        self.eval_cs_marketing_promotion = 0
        self.eval_cs_sales_admin_cost = 0
        self.eval_cs_SGA_total = 0
        self.eval_cs_custom_tax = 0
        self.eval_cs_tax_portion = 0
        self.eval_cs_logistics_costs = 0
        self.eval_cs_warehouse_cost = 0
        self.eval_cs_direct_materials_costs = 0
        self.eval_cs_purchase_total_cost = 0
        self.eval_cs_prod_indirect_labor = 0
        self.eval_cs_prod_indirect_others = 0
        self.eval_cs_direct_labor_costs = 0
        self.eval_cs_depreciation_others = 0
        self.eval_cs_manufacturing_overhead = 0


        # shipped lots count W / M / Q / Y / LifeCycle

        self.shipped_lots_W = [] # 53*plan_range
        self.shipped_lots_M = [] # 12*plan_range
        self.shipped_lots_Q = [] #  4*plan_range
        self.shipped_lots_Y = [] #  1*plan_range
        self.shipped_lots_L = [] #  1  # lifecycle a year

        # Planned Amount
        self.amt_price_sales_shipped =[]
        self.amt_cost_total =[]
        self.amt_profit =[]
        self.amt_marketing_promotion =[]
        self.amt_sales_admin_cost =[]
        self.amt_SGA_total =[]
        self.amt_custom_tax =[]
        self.amt_tax_portion =[]
        self.amt_logistiamt_costs =[]
        self.amt_warehouse_cost =[]
        self.amt_direct_materials_costs =[]
        self.amt_purchase_total_cost =[]
        self.amt_prod_indirect_labor =[]
        self.amt_prod_indirect_others =[]
        self.amt_direct_labor_costs =[]
        self.amt_depreciation_others =[]
        self.amt_manufacturing_overhead =[]

        # shipped amt W / M / Q / Y / LifeCycle

        self.shipped_amt_W = [] # 53*plan_range
        self.shipped_amt_M = [] # 12*plan_range
        self.shipped_amt_Q = [] #  4*plan_range
        self.shipped_amt_Y = [] #  1*plan_range
        self.shipped_amt_L = [] #  1  # lifecycle a year



        # **************************
        # control FLAGs
        # **************************
        self.cost_standard_flag   = 0
        self.PSI_graph_flag       = "OFF"
        self.buffering_stock_flag = "OFF"


        self.revenue     = 0
        self.profit      = 0



# ****************************
# end of Node class definition
# ****************************


# ****************************
# method definition
# ****************************

    def get_all_nodes(self, nodes_list=None):

        if nodes_list is None:

            nodes_list = []

        nodes_list.append(self)

        for child in self.children:

            child.get_all_nodes(nodes_list) # selfを通じて再帰呼び出し

        return nodes_list



    def set_cost_attr(
        self,
        price_sales_shipped,
        cost_total,
        profit,
        marketing_promotion=None,
        sales_admin_cost=None,
        SGA_total=None,
        custom_tax=None,
        tax_portion=None,
        logistics_costs=None,
        warehouse_cost=None,
        direct_materials_costs=None,
        purchase_total_cost=None,
        prod_indirect_labor=None,
        prod_indirect_others=None,
        direct_labor_costs=None,
        depreciation_others=None,
        manufacturing_overhead=None,
    ):

        # self.node_name = node_name # node_name is STOP
        self.price_sales_shipped = price_sales_shipped
        self.cost_total = cost_total
        self.profit = profit
        self.marketing_promotion = marketing_promotion
        self.sales_admin_cost = sales_admin_cost
        self.SGA_total = SGA_total
        self.custom_tax = custom_tax
        self.tax_portion = tax_portion
        self.logistics_costs = logistics_costs
        self.warehouse_cost = warehouse_cost
        self.direct_materials_costs = direct_materials_costs
        self.purchase_total_cost = purchase_total_cost
        self.prod_indirect_labor = prod_indirect_labor
        self.prod_indirect_others = prod_indirect_others
        self.direct_labor_costs = direct_labor_costs
        self.depreciation_others = depreciation_others
        self.manufacturing_overhead = manufacturing_overhead

    def print_cost_attr(self):

        # self.node_name = node_name # node_name is STOP
        print("self.price_sales_shipped", self.price_sales_shipped)
        print("self.cost_total", self.cost_total)
        print("self.profit", self.profit)
        print("self.marketing_promotion", self.marketing_promotion)
        print("self.sales_admin_cost", self.sales_admin_cost)
        print("self.SGA_total", self.SGA_total)
        print("self.custom_tax", self.custom_tax)
        print("self.tax_portion", self.tax_portion)
        print("self.logistics_costs", self.logistics_costs)
        print("self.warehouse_cost", self.warehouse_cost)
        print("self.direct_materials_costs", self.direct_materials_costs)
        print("self.purchase_total_cost", self.purchase_total_cost)
        print("self.prod_indirect_labor", self.prod_indirect_labor)
        print("self.prod_indirect_others", self.prod_indirect_others)
        print("self.direct_labor_costs", self.direct_labor_costs)
        print("self.depreciation_others", self.depreciation_others)
        print("self.manufacturing_overhead", self.manufacturing_overhead)

    def add_child(self, child):

        self.children.append(child)

    def set_parent(self):
        # def set_parent(self, node):

        # treeを辿りながら親ノードを探索
        if self.children == []:

            pass

        else:

            for child in self.children:

                child.parent = self
                # child.parent = node

    # ********************************
    # ココで属性をセット@240417
    # ********************************
    def set_attributes(self, row):

        #print("set_attributes(self, row):", row)
        # self.lot_size = int(row[3])
        # self.leadtime = int(row[4])  # 前提:SS=0
        # self.long_vacation_weeks = eval(row[5])

        self.lot_size = int(row["lot_size"])

        # ********************************
        # with using NetworkX
        # ********************************

        # weightとcapacityは、edge=(node_A,node_B)の属性でnodeで一意ではない

        self.leadtime = int(row["leadtime"])  # 前提:SS=0 # "weight"4NetworkX
        self.capacity = int(row["process_capa"])  # "capacity"4NetworkX

        self.long_vacation_weeks = eval(row["long_vacation_weeks"])

        # **************************
        # BU_SC_node_profile     business_unit_supplychain_node
        # **************************

        # @240421 機械学習のフラグはstop
        ## **************************
        ## plan_basic_parameter ***sequencing is TEMPORARY
        ## **************************
        #        self.PlanningYear           = row['plan_year']
        #        self.plan_engine            = row['plan_engine']
        #        self.reward_sw              = row['reward_sw']

        # 多段階PSIのフラグはstop
        ## ***************************
        ## business unit identify
        ## ***************************
        #        self.product_name           = row['product_name']
        #        self.SC_tree_id             = row['SC_tree_id']
        #        self.node_from              = row['node_from']
        #        self.node_to                = row['node_to']


        # ***************************
        # ココからcost-profit evaluation 用の属性セット
        # ***************************
        self.LT_boat = float(row["LT_boat"])


        # ***************************
        # STOP "V0R2" is NOT apply these attributes / cost_table is defined
        # ***************************
        #self.SGMC_ratio = float(row["SGMC_ratio"])
        #self.Cash_Intrest = float(row["Cash_Intrest"])
        #self.LOT_SIZE = float(row["LOT_SIZE"])
        #self.REVENUE_RATIO = float(row["REVENUE_RATIO"])

        #print("set_plan parameter")
        #print("self.LT_boat", self.LT_boat)

        #print("self.SGMC_ratio", self.SGMC_ratio)
        #print("self.Cash_Intrest", self.Cash_Intrest)
        #print("self.LOT_SIZE", self.LOT_SIZE)
        #print("self.REVENUE_RATIO", self.REVENUE_RATIO)

        # ***************************
        # STOP "V0R2" is NOT apply these attributes / cost_table is defined
        # ***************************
        # **************************
        # product_cost_profile
        # **************************
        #self.PO_Mng_cost = float(row["PO_Mng_cost"])
        #self.Purchase_cost = float(row["Purchase_cost"])
        #self.WH_COST_RATIO = float(row["WH_COST_RATIO"])
        #self.weeks_year = float(row["weeks_year"])
        #self.WH_COST_RATIO_aWeek = float(row["WH_COST_RATIO_aWeek"])

        # print("product_cost_profile parameter")
        # print("self.PO_Mng_cost", self.PO_Mng_cost)
        # print("self.Purchase_cost", self.Purchase_cost)
        # print("self.WH_COST_RATIO", self.WH_COST_RATIO)
        # print("self.weeks_year", self.weeks_year)
        # print("self.WH_COST_RATIO_aWeek", self.WH_COST_RATIO_aWeek)

        # **************************
        # distribution_condition
        # **************************

        #@241231 STOP Refrain from "detailed lot definitions"
        #self.Indivisual_Packing = float(row["Indivisual_Packing"])
        #self.Packing_Lot = float(row["Packing_Lot"])
        #self.Transport_Lot = float(row["Transport_Lot"])
        #self.planning_lot_size = float(row["planning_lot_size"])

        #@STOP
        #self.Distriburion_Cost = float(row["Distriburion_Cost"])  # with NetworkX

        self.SS_days = float(row["SS_days"])


        # print("distribution_condition parameter")
        # print("self.Indivisual_Packing", self.Indivisual_Packing)
        # print("self.Packing_Lot", self.Packing_Lot)
        # print("self.Transport_Lot", self.Transport_Lot)
        # print("self.planning_lot_size", self.planning_lot_size)
        # print("self.Distriburion_Cost", self.Distriburion_Cost)
        # print("self.SS_days", self.SS_days)


        # ***************************
        # STOP "V0R2" is NOT apply these attributes / cost_table is defined
        # ***************************
        ## **************************
        ## TAX_currency_condition # for NetworkX
        ## **************************
        #
        #self.customs_tariff_rate = float(row["customs_tariff_rate"])

        # print("self.HS_code", self.HS_code)
        # print("self.customs_tariff_rate", self.customs_tariff_rate)


        print("row[ customs_tariff_rate ]", row["customs_tariff_rate"])



        self.HS_code              = str(row["HS_code"])
        self.customs_tariff_rate  = float(row["customs_tariff_rate"])
        self.price_elasticity     = float(row["price_elasticity"])



        self.cost_standard_flag   = float(row["cost_standard_flag"])
        self.PSI_graph_flag       = str(row["PSI_graph_flag"])
        self.buffering_stock_flag = str(row["buffering_stock_flag"])

        self.base_leaf = None






    # ********************************
    # setting profit-cost attributes@240417
    # ********************************

    ## ココは、機械学習で使用したEVAL用のcost属性をセットする
    def set_psi_list(self, psi_list):

        self.psi4demand = psi_list

    # supply_plan
    def set_psi_list4supply(self, psi_list):

        self.psi4supply = psi_list


    def get_set_childrenP2S2psi(self, plan_range):

        for child in self.children:

            for w in range(self.leadtime, 53 * plan_range):

                # ******************
                # logistics LT switch
                # ******************
                # 物流をnodeとして定義する場合の表現 STOP
                # 子node childのP [3]のweek positionを親node selfのS [0]にset
                # self.psi4demand[w][0].extend(child.psi4demand[w][3])

                # 物流をLT_shiftで定義する場合の表現 GO
                # childのPのweek positionをLT_shiftして、親nodeのS [0]にset
                ws = w - self.leadtime
                self.psi4demand[ws][0].extend(child.psi4demand[w][3])


    def set_S2psi(self, pSi):

        # S_lots_listが辞書で、node.psiにセットする

        # print("len(self.psi4demand) = ", len(self.psi4demand) )
        # print("len(pSi) = ", len(pSi) )

        for w in range(len(pSi)):  # Sのリスト

            self.psi4demand[w][0].extend(pSi[w])


    def feedback_confirmedS2childrenP(self, plan_range):

        # マザープラントの確定したSを元に、
        # demand_plan上のlot_idの状態にかかわらず、
        # supply_planにおいては、
        # 確定出荷confirmed_Sを元に、以下のpush planを実行する

        # by lotidで一つずつ処理する。

        # 親のconfSのlotidは、どの子nodeから来たのか?
        #  "demand_planのpsi_listのS" の中をサーチしてisin.listで特定する。
        # search_node()では子node psiの中にlotidがあるかisinでcheck

        # LT_shiftして、子nodeのPにplaceする。
        # 親S_lotid => ETA=LT_shift() =>子P[ETA][3]

        # 着荷PをSS_shiftして出荷Sをセット
        # 子P=>SS_shift(P)=>子S

        # Iの生成
        # all_PS2I

        # 親の確定出荷confirmedSをを子供の確定Pとして配分
        # 最後に、conf_PをLT_shiftしてconf_Sにもセットする
        # @230717このLT_shiftの中では、cpnf_Sはmoveする/extendしない

        #
        # def feedback_confirmedS2childrenP(self, plan_range):
        #
        node_req_plans = []
        node_confirmed_plans = []

        self_confirmed_plan = [[] for _ in range(53 * plan_range)]

        # ************************************
        # setting mother_confirmed_plan
        # ************************************
        for w in range(53 * plan_range):

            # 親node自身のsupply_planのpsi_list[w][0]がconfirmed_S
            self_confirmed_plan[w].extend(self.psi4supply[w][0])

        # ************************************
        # setting node_req_plans 各nodeからの要求S(=P)
        # ************************************
        # 子nodeのdemand_planのpsi_list[w][3]のPがS_requestに相当する

        # すべての子nodesから、S_reqをappendしてnode_req_plansを作る
        for child in self.children:

            child_S_req = [[] for _ in range(53 * plan_range)]

            for w in range(53 * plan_range):

                child_S_req[w].extend(child.psi4demand[w][3])  # setting P2S

            node_req_plans.append(child_S_req)

        # node_req_plans      子nodeのP=S要求計画planのリストplans
        # self_confirmed_plan 自nodeの供給計画の確定S

        # 出荷先ごとの出荷計画を求める
        # node_req_plans = [req_plan_node_1, req_plan_node_2, req_plan_node_3]

        # ***************************
        # node 分離
        # ***************************
        node_confirmed_plans = []

        node_confirmed_plans = separated_node_plan(node_req_plans, self_confirmed_plan)

        for i, child in enumerate(self.children):

            for w in range(53 * plan_range):

                # 子nodeのsupply_planのPにmother_plantの確定Sをセット

                child.psi4supply[w][3] = []  # clearing list

                # i番目の子nodeの確定Sをsupply_planのPにextendでlot_idをcopy

                child.psi4supply[w][3].extend(node_confirmed_plans[i][w])

            # ココまででsupply planの子nodeにPがセットされたことになる。

        # *******************************************
        # supply_plan上で、PfixをSfixにPISでLT offsetする
        # *******************************************

        # **************************
        # Safety Stock as LT shift
        # **************************
        safety_stock_week = self.leadtime

        # **************************
        # long vacation weeks
        # **************************
        lv_week = self.long_vacation_weeks

        # P to S の計算処理
        self.psi4supply = shiftP2S_LV(self.psi4supply, safety_stock_week, lv_week)

        ## S to P の計算処理
        # self.psi4demand = shiftS2P_LV(self.psi4demand, safety_stock_week, lv_week)

    def calcPS2I4demand(self):

        # psiS2P = self.psi4demand # copyせずに、直接さわる

        plan_len = 53 * self.plan_range
        # plan_len = len(self.psi4demand)

        for w in range(1, plan_len):  # starting_I = 0 = w-1 / ending_I =plan_len
            # for w in range(1,54): # starting_I = 0 = w-1 / ending_I = 53

            s = self.psi4demand[w][0]
            co = self.psi4demand[w][1]

            i0 = self.psi4demand[w - 1][2]
            i1 = self.psi4demand[w][2]

            p = self.psi4demand[w][3]

            # *********************
            # # I(n-1)+P(n)-S(n)
            # *********************

            work = i0 + p  # 前週在庫と当週着荷分 availables

            # ここで、期末の在庫、S出荷=売上を操作している
            # S出荷=売上を明示的にlogにして、売上として記録し、表示する処理
            # 出荷されたS=売上、在庫I、未出荷COの集合を正しく表現する

            # モノがお金に代わる瞬間 #@240909コこではなくてS実績

            diff_list = [x for x in work if x not in s]  # I(n-1)+P(n)-S(n)

            self.psi4demand[w][2] = i1 = diff_list



    def calcPS2I4supply(self):

        # psiS2P = self.psi4demand # copyせずに、直接さわる

        plan_len = 53 * self.plan_range
        # plan_len = len(self.psi4supply)

        for w in range(1, plan_len):  # starting_I = 0 = w-1 / ending_I =plan_len
            # for w in range(1,54): # starting_I = 0 = w-1 / ending_I = 53

            s = self.psi4supply[w][0]
            co = self.psi4supply[w][1]

            i0 = self.psi4supply[w - 1][2]
            i1 = self.psi4supply[w][2]

            p = self.psi4supply[w][3]

            # *********************
            # # I(n-1)+P(n)-S(n)
            # *********************

            work = i0 + p  # 前週在庫と当週着荷分 availables

            # memo ここで、期末の在庫、S出荷=売上を操作している
            # S出荷=売上を明示的にlogにして、売上として記録し、表示する処理
            # 出荷されたS=売上、在庫I、未出荷COの集合を正しく表現する

            # モノがお金に代わる瞬間

            diff_list = [x for x in work if x not in s]  # I(n-1)+P(n)-S(n)

            self.psi4supply[w][2] = i1 = diff_list

            # ************************************
            # probare a lot checking process
            # ************************************
            
            if self.name == "MUC_N":

                if w in [53,54,55,56,57]:

                    print("s, co, i0, i1, p ", w )
                    print("s" , w, s )
                    print("co", w, co)
                    print("i0", w, i0)
                    print("i1", w, i1)
                    print("p" , w, p )


    def calcPS2I_decouple4supply(self):

        # psiS2P = self.psi4demand # copyせずに、直接さわる

        plan_len = 53 * self.plan_range
        # plan_len = len(self.psi4supply)

        # demand planのSを出荷指示情報=PULL SIGNALとして、supply planSにセット

        for w in range(0, plan_len):
            # for w in range(1,plan_len):

            # pointer参照していないか? 明示的にデータを渡すには?

            self.psi4supply[w][0] = self.psi4demand[w][
                0
            ].copy()  # copy data using copy() method

            # self.psi4supply[w][0]    = self.psi4demand[w][0] # PULL replaced

            # checking pull data
            # show_psi_graph(root_node_outbound,"supply", "HAM", 0, 300 )
            # show_psi_graph(root_node_outbound,"supply", node_show, 0, 300 )

        for w in range(1, plan_len):  # starting_I = 0 = w-1 / ending_I =plan_len

            # demand planSをsupplySにコピー済み
            s = self.psi4supply[w][0]  # PUSH supply S

            co = self.psi4supply[w][1]

            i0 = self.psi4supply[w - 1][2]
            i1 = self.psi4supply[w][2]

            p = self.psi4supply[w][3]

            # *********************
            # # I(n-1)+P(n)-S(n)
            # *********************

            work = i0 + p  # 前週在庫と当週着荷分 availables

            # memo ここで、期末の在庫、S出荷=売上を操作している
            # S出荷=売上を明示的にlogにして、売上として記録し、表示する処理
            # 出荷されたS=売上、在庫I、未出荷COの集合を正しく表現する

            # モノがお金に代わる瞬間

            diff_list = [x for x in work if x not in s]  # I(n-1)+P(n)-S(n)

            self.psi4supply[w][2] = i1 = diff_list

    def calcS2P(self): # backward planning

        # **************************
        # Safety Stock as LT shift
        # **************************
        # leadtimeとsafety_stock_weekは、ここでは同じ

        # 同一node内なので、ssのみで良い
        shift_week = int(round(self.SS_days / 7))

        ## stop 同一node内でのLT shiftは無し
        ## SS is rounded_int_num
        # shift_week = self.leadtime +  int(round(self.SS_days / 7))

        # **************************
        # long vacation weeks
        # **************************
        lv_week = self.long_vacation_weeks

        # 同じnode内でのS to P の計算処理 # backward planning
        self.psi4demand = shiftS2P_LV(self.psi4demand, shift_week, lv_week)

        pass


    def calcS2P_4supply(self):    # "self.psi4supply"
        # **************************
        # Safety Stock as LT shift
        # **************************
        # leadtimeとsafety_stock_weekは、ここでは同じ

        # 同一node内なので、ssのみで良い
        shift_week = int(round(self.SS_days / 7))

        ## stop 同一node内でのLT shiftは無し
        ## SS is rounded_int_num
        # shift_week = self.leadtime +  int(round(self.SS_days / 7))

        # **************************
        # long vacation weeks
        # **************************
        lv_week = self.long_vacation_weeks

        # S to P の計算処理
        self.psi4supply = shiftS2P_LV_replace(self.psi4supply, shift_week, lv_week)

        pass


    def set_plan_range_lot_counts(self, plan_range, plan_year_st):

        # print("node.plan_range", self.name, self.plan_range)

        self.plan_range = plan_range
        self.plan_year_st = plan_year_st

        self.lot_counts = [0 for x in range(0, 53 * self.plan_range)]

        # ******************************
        # set_EVAL_cash_in_data #list for 53weeks * 5 years # 5年を想定
        # *******************************
        self.Profit = Profit = [0 for i in range(53 * self.plan_range)]
        self.Week_Intrest = Week_Intrest = [0 for i in range(53 * self.plan_range)]
        self.Cash_In = Cash_In = [0 for i in range(53 * self.plan_range)]
        self.Shipped_LOT = Shipped_LOT = [0 for i in range(53 * self.plan_range)]
        self.Shipped = Shipped = [0 for i in range(53 * self.plan_range)]

        # ******************************
        # set_EVAL_cash_out_data #list for 54 weeks
        # ******************************

        self.SGMC = SGMC = [0 for i in range(53 * self.plan_range)]
        self.PO_manage = PO_manage = [0 for i in range(53 * self.plan_range)]
        self.PO_cost = PO_cost = [0 for i in range(53 * self.plan_range)]
        self.P_unit = P_unit = [0 for i in range(53 * self.plan_range)]
        self.P_cost = P_cost = [0 for i in range(53 * self.plan_range)]

        self.I = I = [0 for i in range(53 * self.plan_range)]

        self.I_unit = I_unit = [0 for i in range(53 * self.plan_range)]
        self.WH_cost = WH_cost = [0 for i in range(53 * self.plan_range)]
        self.Dist_Cost = Dist_Cost = [0 for i in range(53 * self.plan_range)]

        for child in self.children:

            child.set_plan_range_lot_counts(plan_range, plan_year_st)

    # ******************************
    # evaluation 操作
    # ******************************
    # ******************************
    # EvalPlanSIP  rewardを計算
    # ******************************


    def set_shipped_lots_count(self):

        plan_len = 53 * self.plan_range

        #print("node.name", self.name )
        #print("psi4supply ", self.psi4supply )

        for w in range(0, plan_len-1):  ### 以下のi+1で1週スタート = W1,W2,W3,,


            #@MEMO
            # 出荷実績は、min(I+P, S)で算定する


            self.shipped_lots_W.append( 
                min( (len(self.psi4supply[w][2]) + len(self.psi4supply[w][3])),
                     len(self.psi4supply[w][0])
                )
            )



       #print("node.name shipped_lots_W ", self.name, self.shipped_lots_W )



    def set_lot_counts(self):

        plan_len = 53 * self.plan_range

        for w in range(0, plan_len):  ### 以下のi+1で1週スタート = W1,W2,W3,,
            self.lot_counts[w] = len(self.psi4supply[w][3])  # psi[w][3]=PO

        self.lot_counts_all = sum(self.lot_counts)



    def I_lot_counts_all(self):
        lot_all_supply = 0
        lot_all_demand = 0

        plan_len = 53 * self.plan_range

        lot_counts_I_supply = [0] * plan_len
        lot_counts_I_demand = [0] * plan_len

        #@241129 DEBUG DUMP TEST self.psi4supply
        #if self.name == "HAM":
        #    print("self.psi4supply",self.psi4supply)




        for w in range(plan_len):  ### 以下のi+1で1週スタート = W1,W2,W3,,
            lot_counts_I_supply[w] = len(self.psi4supply[w][2])  # psi[w][2]=I
            lot_counts_I_demand[w] = len(self.psi4demand[w][2])  # psi[w][2]=I


        #@241129 DUMP TEST self.psi4supply
        if self.name == "HAM":
            print("lot_counts_I_supply",lot_counts_I_supply)



        lot_all_supply = sum(lot_counts_I_supply)
        lot_all_demand = sum(lot_counts_I_demand)

        return lot_all_supply, lot_all_demand






    def EvalPlanSIP_cost_table(self):

        plan_len = 53 * self.plan_range

        for i in range(0, plan_len - 1):  
        ###以下のi+1で1週スタート = W1,W2,W3,,,

            ### i+1 = W1,W2,W3,,,


            self.amt_price_sales_shipped.append(self.shipped_lots_W[i] * self.cs_price_sales_shipped )
            self.amt_cost_total.append(self.shipped_lots_W[i] * self.cs_cost_total )
            self.amt_profit.append(self.shipped_lots_W[i] * self.cs_profit )
            self.amt_marketing_promotion.append(self.shipped_lots_W[i] * self.cs_marketing_promotion )
            self.amt_sales_admin_cost.append(self.shipped_lots_W[i] * self.cs_sales_admin_cost )
            self.amt_SGA_total.append(self.shipped_lots_W[i] * self.cs_SGA_total )
            self.amt_custom_tax.append(self.shipped_lots_W[i] * self.cs_custom_tax )
            self.amt_tax_portion.append(self.shipped_lots_W[i] * self.cs_tax_portion )
            self.amt_logistiamt_costs.append(self.shipped_lots_W[i] * self.cs_logistics_costs )
            self.amt_warehouse_cost.append(self.shipped_lots_W[i] * self.cs_warehouse_cost )
            self.amt_direct_materials_costs.append(self.shipped_lots_W[i] * self.cs_direct_materials_costs )
            self.amt_purchase_total_cost.append(self.shipped_lots_W[i] * self.cs_purchase_total_cost )
            self.amt_prod_indirect_labor.append(self.shipped_lots_W[i] * self.cs_prod_indirect_labor )
            self.amt_prod_indirect_others.append(self.shipped_lots_W[i] * self.cs_prod_indirect_others )
            self.amt_direct_labor_costs.append(self.shipped_lots_W[i] * self.cs_direct_labor_costs )
            self.amt_depreciation_others.append(self.shipped_lots_W[i] * self.cs_depreciation_others )
            self.amt_manufacturing_overhead.append(self.shipped_lots_W[i] * self.cs_manufacturing_overhead )




            # ********************************
            # 売切る商売や高級店ではPROFITをrewardに使うことが想定される
            # ********************************
            self.eval_profit = sum(self.amt_profit[1:])  # *** PROFIT

            # ********************************
            # 前線の小売りの場合、revenueをrewardに使うことが想定される
            # ********************************
            self.eval_revenue = sum(self.amt_price_sales_shipped[1:])  #REVENUE

            ## revenu
            #self.amt_price_sales_shipped
            #
            ## profit
            #self.amt_profit

            # profit_ratio
            # ********************************
            # 一般的にはprofit ratioをrewardに使うことが想定される
            # ********************************
            if sum(self.amt_price_sales_shipped[1:]) == 0:

               #print("error: sum(self.amt_price_sales_shipped[1:]) == 0")

                self.eval_profit_ratio = 0

            else:

                self.eval_profit_ratio = sum(self.amt_profit[1:]) / sum(self.amt_price_sales_shipped[1:])

            #self.eval_profit_ratio = sum(self.amt_profit[1:]) / sum(self.amt_price_sales_shipped[1:])



       #print("self.amt_price_sales_shipped    ",self.amt_price_sales_shipped    )
       #print("self.amt_cost_total             ",self.amt_cost_total             )
       #print("self.amt_profit                 ",self.amt_profit                 )
       #print("self.amt_marketing_promotion    ",self.amt_marketing_promotion    )
       #print("self.amt_sales_admin_cost       ",self.amt_sales_admin_cost       )
       #print("self.amt_SGA_total              ",self.amt_SGA_total              )
       #print("self.amt_custom_tax             ",self.amt_custom_tax             )
       #print("self.amt_tax_portion            ",self.amt_tax_portion            )
       #print("self.amt_logistiamt_costs       ",self.amt_logistiamt_costs       )
       #print("self.amt_warehouse_cost         ",self.amt_warehouse_cost         )
       #print("self.amt_direct_materials_costs ",self.amt_direct_materials_costs )
       #print("self.amt_purchase_total_cost    ",self.amt_purchase_total_cost    )
       #print("self.amt_prod_indirect_labor    ",self.amt_prod_indirect_labor    )
       #print("self.amt_prod_indirect_others   ",self.amt_prod_indirect_others   )
       #print("self.amt_direct_labor_costs     ",self.amt_direct_labor_costs     )
       #print("self.amt_depreciation_others    ",self.amt_depreciation_others    )
       #print("self.amt_manufacturing_overhead ",self.amt_manufacturing_overhead )




    def EvalPlanSIP(self):

        plan_len = 53 * self.plan_range

        for i in range(0, 53 * self.plan_range):  ###以下のi+1で1週スタート = W1,W2,W3,,,

            # calc PO_manage 各週の(梱包単位)LOT数をカウントし輸送ロットで丸め
            # =IF(SUM(G104:G205)=0,0,QUOTIENT(SUM(G104:G205),$C$17)+1)

            ### i+1 = W1,W2,W3,,,

            if self.lot_counts[i] == 0:  ## ロットが発生しない週の分母=0対応
                self.PO_manage[i] = 0
            else:

                self.PO_manage[i] = self.lot_counts[i] // self.Transport_Lot + 1

            # Distribution Cost =$C$19*G12
            self.Dist_Cost[i] = self.Distriburion_Cost * self.PO_manage[i]

            # 在庫self.I_year[w] <=> 在庫self.psi4supply[w][2]
            # Inventory UNIT =G97/$C$7
            # self.I_unit[i]  = self.I_year[i] / self.planning_lot_size

            # print("EvalPlanSIP len(self.psi4supply[i][2])", self.name, len(self.psi4supply[i][2]), self.psi4supply[i][2], self.planning_lot_size )

            self.I_unit[i] = len(self.psi4supply[i][2]) / float(self.planning_lot_size)


            #@241229 KOKODA
            # ******************************************************
            # 前提: 在庫日数=14日=2weeksの時のWH_COSTを在庫コストの基準とする
            # ******************************************************


            # WH_COST by WEEK =G19*$C$11*$C$8
            self.WH_cost[i] = (
                float(self.I_unit[i]) * self.WH_COST_RATIO * self.REVENUE_RATIO
            )




            # Purchase by UNIT =G98/$C$7
            # self.P_unit[i]    = self.P_year[i] / self.planning_lot_size

            self.P_unit[i] = len(self.psi4supply[i][3]) / float(self.planning_lot_size)

            # Purchase Cost =G15*$C$8*$C$10
            self.P_cost[i] = (
                float(self.P_unit[i]) * self.Purchase_cost * self.REVENUE_RATIO
            )

            # PO manage cost =G15*$C$9*$C$8 ### PO_manage => P_unit
            ### self.PO_manage[i] = self.PO_manage[i] ###
            self.PO_cost[i] = self.P_unit[i] * self.PO_Mng_cost * self.REVENUE_RATIO
            #            # PO manage cost =G12*$C$9*$C$8
            #            self.PO_cost[i]   = self.PO_manage[i] * self.PO_Mng_cost * self.REVENUE_RATIO

            # =MIN(G95+G96,G97+G98) shipped
            # self.Shipped[i] = min( self.S_year[i] + self.CO_year[i] , self.I_year[i] + self.IP_year[i] )

            self.Shipped[i] = min(
                len(self.psi4supply[i][0]) + len(self.psi4supply[i][1]),
                len(self.psi4supply[i][2]) + len(self.psi4supply[i][3]),
            )

            # =G9/$C$7 shipped UNIT
            # self.Shipped_LOT[i] = self.Shipped[i] / self.planning_lot_size

            # @240424 memo すでにlot_sizeでの丸めは処理されているハズ
            self.Shipped_LOT[i] = self.Shipped[i]  ###**/ self.planning_lot_size

            # =$C$8*G8 Cach In
            self.Cash_In[i] = self.REVENUE_RATIO * self.Shipped_LOT[i]

            # =$C$6*(52-INT(RIGHT(G94,LEN(G94)-1)))/52 Week_Intrest Cash =5%/52
            self.Week_Intrest[i] = self.Cash_Intrest * (52 - (i)) / 52

            # =G7*$C$5 Sales and General managnt cost
            self.SGMC[i] = self.Cash_In[i] * self.SGMC_ratio

            # =G7*(1+G6)-G13-G16-G20-G5-G21 Profit
            self.Profit[i] = (
                self.Cash_In[i] * (1 + self.Week_Intrest[i])
                - self.PO_cost[i]
                - self.P_cost[i]
                - self.WH_cost[i]
                - self.SGMC[i]
                - self.Dist_Cost[i]
            )

        # ******************************
        # reward 切り替え
        # ******************************
        # =SUM(H4:BH4)/SUM(H7:BH7) profit_ratio
        if sum(self.Cash_In[1:]) == 0:
            self.eval_profit_ratio = 0
        else:

            # ********************************
            # 売切る商売や高級店ではPROFITをrewardに使うことが想定される
            # ********************************
            self.eval_profit = sum(self.Profit[1:])  # *** PROFIT

            # ********************************
            # 前線の小売りの場合、revenueをrewardに使うことが想定される
            # ********************************
            self.eval_revenue = sum(self.Cash_In[1:])  # *** REVENUE

            self.eval_PO_cost = sum(self.PO_cost[1:])
            self.eval_P_cost = sum(self.P_cost[1:])
            self.eval_WH_cost = sum(self.WH_cost[1:])
            self.eval_SGMC = sum(self.SGMC[1:])
            self.eval_Dist_Cost = sum(self.Dist_Cost[1:])

            # ********************************
            # 一般的にはprofit ratioをrewardに使うことが想定される
            # ********************************
            self.eval_profit_ratio = sum(self.Profit[1:]) / sum(self.Cash_In[1:])

        # print("")
        # print("Eval node", self.name)
        # print("profit       ", self.eval_profit)

        # print("PO_cost      ", self.eval_PO_cost)
        # print("P_cost       ", self.eval_P_cost)
        # print("WH_cost      ", self.eval_WH_cost)
        # print("SGMC         ", self.eval_SGMC)
        # print("Dist_Cost    ", self.eval_Dist_Cost)

        # print("revenue      ", self.eval_revenue)
        # print("profit_ratio ", self.eval_profit_ratio)


# cut and paste


    def EvalPlanSIP_cost(self):

        L = self.lot_counts_all    # nodeの全ロット数 # psi[w][3]=PO
    
        # evaluated cost = Cost Structure X lot_counts
        self.eval_cs_price_sales_shipped    = L * self.cs_price_sales_shipped
        self.eval_cs_cost_total             = L * self.cs_cost_total
        self.eval_cs_profit                 = L * self.cs_profit
        self.eval_cs_marketing_promotion    = L * self.cs_marketing_promotion
        self.eval_cs_sales_admin_cost       = L * self.cs_sales_admin_cost
        self.eval_cs_SGA_total              = L * self.cs_SGA_total
        self.eval_cs_custom_tax             = L * self.cs_custom_tax
        self.eval_cs_tax_portion            = L * self.cs_tax_portion
        self.eval_cs_logistics_costs        = L * self.cs_logistics_costs
        self.eval_cs_warehouse_cost         = L * self.cs_warehouse_cost
        self.eval_cs_direct_materials_costs = L * self.cs_direct_materials_costs    
        self.eval_cs_purchase_total_cost    = L * self.cs_purchase_total_cost
        self.eval_cs_prod_indirect_labor    = L * self.cs_prod_indirect_labor
        self.eval_cs_prod_indirect_others   = L * self.cs_prod_indirect_others
        self.eval_cs_direct_labor_costs     = L * self.cs_direct_labor_costs
        self.eval_cs_depreciation_others    = L * self.cs_depreciation_others
        self.eval_cs_manufacturing_overhead = L * self.cs_manufacturing_overhead    
    
        # 在庫係数の計算
        I_total_qty_planned, I_total_qty_init = self.I_lot_counts_all() 
    
        if I_total_qty_init == 0:

            I_cost_coeff = 0

        else:

            I_cost_coeff =  I_total_qty_planned / I_total_qty_init
    
        print("self.name",self.name)
        print("I_total_qty_planned", I_total_qty_planned)
        print("I_total_qty_init", I_total_qty_init)
        print("I_cost_coeff", I_cost_coeff)
    
        # 在庫の増減係数を掛けてセット

        print("self.eval_cs_warehouse_cost", self.eval_cs_warehouse_cost)

        self.eval_cs_warehouse_cost *= ( 1 + I_cost_coeff )

        print("self.eval_cs_warehouse_cost", self.eval_cs_warehouse_cost)

    
        self.eval_cs_cost_total = (

            self.eval_cs_marketing_promotion + 
            self.eval_cs_sales_admin_cost + 
            #self.eval_cs_SGA_total + 

            #self.eval_cs_custom_tax + 
            self.eval_cs_tax_portion + 
            self.eval_cs_logistics_costs + 
            self.eval_cs_warehouse_cost + 
            self.eval_cs_direct_materials_costs + 
            #self.eval_cs_purchase_total_cost + 

            self.eval_cs_prod_indirect_labor + 
            self.eval_cs_prod_indirect_others + 
            self.eval_cs_direct_labor_costs + 
            self.eval_cs_depreciation_others #@END + 
            #self.eval_cs_manufacturing_overhead
        )
    
        # profit = revenue - cost
        self.eval_cs_profit = self.eval_cs_price_sales_shipped - self.eval_cs_cost_total
    
        return self.eval_cs_price_sales_shipped, self.eval_cs_profit




    # *****************************
    # ここでCPU_LOTsを抽出する
    # *****************************
    def extract_CPU(self, csv_writer):

        plan_len = 53 * self.plan_range  # 計画長をセット

        # w=1から抽出処理

        # starting_I = 0 = w-1 / ending_I=plan_len
        for w in range(1, plan_len):

            # for w in range(1,54):   #starting_I = 0 = w-1 / ending_I = 53

            s = self.psi4supply[w][0]

            co = self.psi4supply[w][1]

            i0 = self.psi4supply[w - 1][2]
            i1 = self.psi4supply[w][2]

            p = self.psi4supply[w][3]

            # ***************************
            # write CPU
            # ***************************
            #
            # ISO_week_no,
            # CPU_lot_id,
            # S-I-P区分,
            # node座標(longitude, latitude),
            # step(高さ=何段目),
            # lot_size
            # ***************************

            # ***************************
            # write "s" CPU
            # ***************************
            for step_no, lot_id in enumerate(s):

                # lot_idを計画週YYYYWWでユニークにする
                lot_id_yyyyww = lot_id + str(self.plan_year_st) + str(w).zfill(3)

                CPU_row = [
                    w,
                    lot_id_yyyyww,
                    "s",
                    self.name,
                    self.longitude,
                    self.latitude,
                    step_no,
                    self.lot_size,
                ]

                csv_writer.writerow(CPU_row)

            # ***************************
            # write "i1" CPU
            # ***************************
            for step_no, lot_id in enumerate(i1):

                # lot_idを計画週YYYYWWでユニークにする
                lot_id_yyyyww = lot_id + str(self.plan_year_st) + str(w).zfill(3)

                CPU_row = [
                    w,
                    lot_id_yyyyww,
                    "i1",
                    self.name,
                    self.longitude,
                    self.latitude,
                    step_no,
                    self.lot_size,
                ]

                csv_writer.writerow(CPU_row)

            # ***************************
            # write "p" CPU
            # ***************************
            for step_no, lot_id in enumerate(p):

                # lot_idを計画週YYYYWWでユニークにする
                lot_id_yyyyww = lot_id + str(self.plan_year_st) + str(w).zfill(3)

                CPU_row = [
                    w,
                    lot_id_yyyyww,
                    "p",
                    self.name,
                    self.longitude,
                    self.latitude,
                    step_no,
                    self.lot_size,
                ]

                csv_writer.writerow(CPU_row)

            ## *********************
            ## s checking demand_lot_idのリスト
            ## *********************
            # if w == 100:
            #
            #    print('checking w100 s',s)


    # ******************
    # for debug
    # ******************
    def show_sum_cs(self):

        cs_sum = 0

        cs_sum = (
            self.cs_direct_materials_costs
            + self.cs_marketing_promotion
            + self.cs_sales_admin_cost
            + self.cs_tax_portion
            + self.cs_logistics_costs
            + self.cs_warehouse_cost
            + self.cs_prod_indirect_labor
            + self.cs_prod_indirect_others
            + self.cs_direct_labor_costs
            + self.cs_depreciation_others
            + self.cs_profit
        )

       #print("cs_sum", self.name, cs_sum)






# ****************************
# supply chain tree creation
# ****************************
def create_tree_set_attribute(file_name):

    # 深さと幅に対応
    # Pythonのcollections.defaultdictは、
    # 存在しないキーに対するアクセス時にデフォルト値を自動的に生成する辞書
    # この場合、intを渡しているので、存在しないキーに対するデフォルト値は0

    width_tracker = defaultdict(int)  # 各深さで使用済みの幅を追跡する辞書

    root_node_name = ""  # init setting

    with open(file_name, "r", encoding="utf-8-sig") as f:

        reader = csv.DictReader(f)  # header行の項目名をkeyにして、辞書生成

        # for row in reader:

        # デフォルトでヘッダー行はスキップされている
        # next(reader)  # ヘッダー行をスキップ

        # nodeインスタンスの辞書を作り、親子の定義に使う
        # nodes = {row[2]: Node(row[2]) for row in reader}
        nodes = {row["child_node_name"]: Node(row["child_node_name"]) for row in reader}

        f.seek(0)  # ファイルを先頭に戻す
        next(reader)  # ヘッダー行をスキップ

        for row in reader:

            # if row[0] == "root":
            if row["Parent_node"] == "root":

                # root_node_name = row[1]
                root_node_name = row["Child_node"]

                root = nodes[root_node_name]
                root.width += 4

            else:

                # print("row['Parent_node'] ", row["Parent_node"])

                # parent = nodes[row[0]]
                parent = nodes[row["Parent_node"]]

                # child = nodes[row[1]]
                child = nodes[row["Child_node"]]

                parent.add_child(child)

                # @STOP
                ## 深さと幅に対応
                ## width_trackerを引数として渡す
                # parent.add_child(child, width_tracker)

                child.set_attributes(row)

    return nodes, root_node_name  # すべてのインスタンス・ポインタを返して使う



def set_parent_all(node):
    # preordering

    if node.children == []:
        pass
    else:
        node.set_parent()  # この中で子nodeを見て親を教える。
        # def set_parent(self)

    for child in node.children:

        set_parent_all(child)




def print_parent_all(node):
    # preordering

    if node.children == []:
        pass
    else:
        print("node.parent and children", node.name, node.children)

    for child in node.children:

        print("child and parent", child.name, node.name)

        print_parent_all(child)




# ******************************
# cost setting
# ******************************
# ******************************
# cost setting
# ******************************
def read_set_cost(cost_table, nodes_outbound):

    # CSVファイルを読み込む
    df = pd.read_csv(cost_table)

    # 行列を入れ替える
    df_transposed = df.transpose()

    #print("df_transposed", df_transposed)

    # iterrows()が返すイテレータを取得
    rows = df_transposed.iterrows()

    # 最初の行をスキップ（next関数を使用）
    next(rows)

    # 残りの行を反復処理
    for index, row in rows:
        # for index, row in df_transposed.iterrows():

        #print("index and row[0]", index, row[0])
        #print("index and row", index, row)

        node_name = index

        try:
            node = nodes_outbound[node_name]
            node.set_cost_attr(*row)
            node.print_cost_attr()
        except KeyError:
            # nodes_outboundにキーが存在しない場合は処理をスキップ
            print(f"Warning: {node_name} not found in nodes_outbound. Continuing with next item.")
            pass



def read_set_cost_OLD(cost_table, nodes_outbound):

    # CSVファイルを読み込む
    df = pd.read_csv(cost_table)

    # 行列を入れ替える
    df_transposed = df.transpose()

    #print("df_transposed", df_transposed)

    # iterrows()が返すイテレータを取得
    rows = df_transposed.iterrows()

    # 最初の行をスキップ（next関数を使用）
    next(rows)

    # 残りの行を反復処理
    for index, row in rows:
        # for index, row in df_transposed.iterrows():

        #print("index and row[0]", index, row[0])
        #print("index and row", index, row)

        node_name = index

        if nodes_outbound[node_name] :

            node = nodes_outbound[node_name]
            node.set_cost_attr(*row)

        else:

            print("error: unmatch node in cost_table and profile")

        node.print_cost_attr()



# *********************************
# check_plan_range
# *********************************
def check_plan_range(df):  # df is dataframe

    #
    # getting start_year and end_year
    #
    start_year = node_data_min = df["year"].min()
    end_year = node_data_max = df["year"].max()

    # *********************************
    # plan initial setting
    # *********************************

    plan_year_st = int(start_year)  # 2024  # plan開始年

    # 3ヵ年または5ヵ年計画分のS計画を想定
    plan_range = int(end_year) - int(start_year) + 1 + 1  # +1はハミ出す期間

    plan_year_end = plan_year_st + plan_range

    return plan_range, plan_year_st


# 2. lot_id_list列を追加
def generate_lot_ids(row):

    # node_yyyy_ww = f"{row['node_name']}_{row['iso_year']}_{row['iso_week']}"
    node_yyyy_ww = f"{row['node_name']}{row['iso_year']}{row['iso_week']}"

    lots_count = row["S_lot"]

    # stack_list = [f"{node_yyyy_ww}_{i}" for i in range(lots_count)]

    #@240930 修正MEMO
    # ココの{i}をzfillで二桁にする
    #stack_list = [f"{node_yyyy_ww}{i:02}" for i in range(lots_count)]

    digit_count = 2
    stack_list = [f"{node_yyyy_ww}{str(i).zfill(digit_count)}" for i in range(lots_count)]

    return stack_list




# ******************************
# trans month 2 week 2 lot_id_list
# ******************************
def trans_month2week2lot_id_list(file_name, lot_size):

    df = pd.read_csv(file_name)

    # *********************************
    # check_plan_range
    # *********************************
    plan_range, plan_year_st = check_plan_range(df)  # df is dataframe

    df = df.melt(
        id_vars=["product_name", "node_name", "year"],
        var_name="month",
        value_name="value",
    )

    df["month"] = df["month"].str[1:].astype(int)

    df_daily = pd.DataFrame()

    for _, row in df.iterrows():

        daily_values = np.full(
            pd.Timestamp(row["year"], row["month"], 1).days_in_month, row["value"]
        )

        dates = pd.date_range(
            start=f"{row['year']}-{row['month']}-01", periods=len(daily_values)
        )

        df_temp = pd.DataFrame(
            {
                "product_name": row["product_name"],
                "node_name": row["node_name"],
                "date": dates,
                "value": daily_values,
            }
        )

        df_daily = pd.concat([df_daily, df_temp])


    #@24240930 STOP
    #df_daily["iso_year"] = df_daily["date"].dt.isocalendar().year
    #df_daily["iso_week"] = df_daily["date"].dt.isocalendar().week
    #
    #df_weekly = (
    #    df_daily.groupby(["product_name", "node_name", "iso_year", "iso_week"])["value"]
    #    .sum()
    #    .reset_index()
    #)


    df_daily["iso_year"] = df_daily["date"].dt.isocalendar().year

    # ISO週を２ケタ表示
    df_daily["iso_week"] = df_daily["date"].dt.isocalendar().week.astype(str).str.zfill(2)

    df_weekly = (
        df_daily.groupby(["product_name", "node_name", "iso_year", "iso_week"])["value"]
        .sum()
        .reset_index()
    )

    ## 1. S_lot列を追加
    # lot_size = 100  # ここに適切なlot_sizeを設定します
    df_weekly["S_lot"] = df_weekly["value"].apply(lambda x: math.ceil(x / lot_size))

    ## 2. lot_id_list列を追加
    # def generate_lot_ids(row):
    df_weekly["lot_id_list"] = df_weekly.apply(generate_lot_ids, axis=1)

    return df_weekly, plan_range, plan_year_st




# ******************************
# 深さと幅を値 setting balance
# ******************************
def set_positions(root):
    width_tracker = [0] * 100  # 深さの最大値を100と仮定
    set_positions_recursive(root, width_tracker)
    adjust_positions(root)


def set_positions_recursive(node, width_tracker):
    for child in node.children:
        child.depth = node.depth + 1
        child.width = width_tracker[child.depth]
        width_tracker[child.depth] += 1
        set_positions_recursive(child, width_tracker)


def adjust_positions(node):
    if not node.children:
        return node.width

    children_y_min = min(adjust_positions(child) for child in node.children)
    children_y_max = max(adjust_positions(child) for child in node.children)
    node.width = (children_y_min + children_y_max) / 2

    # Y軸の位置を調整
    for i, child in enumerate(node.children):
        child.width += i * 0.1  # 重複を避けるために少しずつずらす


    return node.width



def find_all_paths(node, path, paths):
    path.append(node.name)

    if not node.children:

        #print("leaf path", node.name, path)
        paths.append(path.copy())

    else:

        for child in node.children:

            # print("child path",child.name, path)

            find_all_paths(child, path, paths)

            for grandchild in child.children:
                #print("grandchild path", grandchild.name, path)
                find_all_paths(grandchild, path, paths)

                for g_grandchild in grandchild.children:
                    #print("g_grandchild path", g_grandchild.name, path)
                    find_all_paths(g_grandchild, path, paths)

                    for g1_grandchild in g_grandchild.children:
                        #print("g1_grandchild path", g1_grandchild.name, path)
                        find_all_paths(g1_grandchild, path, paths)

                        for g2_grandchild in g1_grandchild.children:
                            #print("g2_grandchild path", g2_grandchild.name, path)
                            find_all_paths(g2_grandchild, path, paths)

    path.pop()


def find_paths(root):

    paths = []

    find_all_paths(root, [], paths)

    return paths


def make_capa_year_month(input_file):

    #    # mother plant capacity parameter
    #    demand_supply_ratio = 1.2  # demand_supply_ratio = ttl_supply / ttl_demand

    # initial setting of total demand and supply
    # total_demandは、各行のm1からm12までの列の合計値

    df_capa = pd.read_csv(input_file)

    df_capa["total_demand"] = df_capa.iloc[:, 3:].sum(axis=1)

    # yearでグループ化して、月次需要数の総和を計算
    df_capa_year = df_capa.groupby(["year"], as_index=False).sum()

    return df_capa_year


# ****************************
# 辞書をinbound tree nodeのdemand listに接続する
# ****************************
def set_dict2tree_psi(node, attr_name, node_psi_dict):

    setattr(node, attr_name, node_psi_dict.get(node.name))

    # node.psi4supply = node_psi_dict.get(node.name)

    for child in node.children:

        set_dict2tree_psi(child, attr_name, node_psi_dict)


# nodeを手繰りながらnode_psi_dict辞書を初期化する
def make_psi_space_dict(node, node_psi_dict, plan_range):

    psi_list = [[[] for j in range(4)] for w in range(53 * plan_range)]

    node_psi_dict[node.name] = psi_list  # 新しいdictにpsiをセット

    for child in node.children:

        make_psi_space_dict(child, node_psi_dict, plan_range)

    return node_psi_dict




# sliced df をcopyに変更
def make_lot_id_list_list(df_weekly, node_name):
    # 指定されたnode_nameがdf_weeklyに存在するか確認
    if node_name not in df_weekly["node_name"].values:
        return "Error: The specified node_name does not exist in df_weekly."

    # node_nameに基づいてデータを抽出
    df_node = df_weekly[df_weekly["node_name"] == node_name].copy()

    # 'iso_year'列と'iso_week'列を結合して新しいキーを作成
    df_node.loc[:, "iso_year_week"] = df_node["iso_year"].astype(str) + df_node[
        "iso_week"
    ].astype(str)

    # iso_year_weekでソート
    df_node = df_node.sort_values("iso_year_week")

    # lot_id_listのリストを生成
    pSi = [lot_id_list for lot_id_list in df_node["lot_id_list"]]

    return pSi




# dfを渡す
def set_df_Slots2psi4demand(node, df_weekly):
    # def set_psi_lists_postorder(node, node_psi_dict):


    #@240930
    #print("df_weekly@240930",df_weekly)

# an image of "df_weekly"
#
#df_weekly@240930      product_name node_name  ...  S_lot                   lot_id_list
#0          prod-A       CAN  ...      0                            []
#1          prod-A       CAN  ...      0                            []
#2          prod-A       CAN  ...      0                            []
#3          prod-A       CAN  ...      0                            []
#4          prod-A       CAN  ...      0                            []
#...           ...       ...  ...    ...                           ...
#1850       prod-A     SHA_N  ...      2  [SHA_N2024490, SHA_N2024491]
#1851       prod-A     SHA_N  ...      2  [SHA_N2024500, SHA_N2024501]
#1852       prod-A     SHA_N  ...      2  [SHA_N2024510, SHA_N2024511]
#1853       prod-A     SHA_N  ...      2  [SHA_N2024520, SHA_N2024521]
#1854       prod-A     SHA_N  ...      1                 [SHA_N202510]
#









    for child in node.children:

        set_df_Slots2psi4demand(child, df_weekly)

    # leaf_node末端市場の判定
    if node.children == []:  # 子nodeがないleaf nodeの場合

        # df_weeklyからnode.nameで、pSi[w]=lot_id_listとなるlistを作る
        # node.nameが存在しない場合はerror

        # nodeのSリスト pSi[w]を作る
        pSi = make_lot_id_list_list(df_weekly, node.name)


        ## probare 
        ##@240929
        #if node.name == "MUC_I":
        #    print("node.name pSi set_df_Slots2psi4demand")
        #    print("node.name pSi set_df_Slots2psi4demand",node.name, pSi)


#@240929 
# 1. lot_idの定義yyyywwnnに合せる
# 2. list position[]と"yyyyww"は、"start_year+week_no"と整合させる
# 3. find_yyyyww(start_year,week_no)でyyyywwを、find_week_no(start_year,yyyyww)
#    を、初期処理で、固定tableで用意する
#node.name pSi set_df_Slots2psi4demand MUC_I [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], ['MUC_I202410'], ['MUC_I2024100'], ['MUC_I2024110'], ['MUC_I2024120'], ['MUC_I2024130'], ['MUC_I2024140'], ['MUC_I2024150'], ['MUC_I2024160'], ['MUC_I2024170'], ['MUC_I2024180'], ['MUC_I2024190'], ['MUC_I202420'], ['MUC_I2024200'], ['MUC_I2024210'], ['MUC_I2024220'], ['MUC_I2024230'], ['MUC_I2024240'], ['MUC_I2024250'], ['MUC_I2024260'], ['MUC_I2024270'], ['MUC_I2024280'], ['MUC_I2024290'], ['MUC_I202430'], ['MUC_I2024300'], ['MUC_I2024310'], ['MUC_I2024320'], ['MUC_I2024330'], ['MUC_I2024340'], ['MUC_I2024350'], ['MUC_I2024360'], ['MUC_I2024370'], ['MUC_I2024380'], ['MUC_I2024390'], ['MUC_I202440'], ['MUC_I2024400'], ['MUC_I2024410'], ['MUC_I2024420'], ['MUC_I2024430'], ['MUC_I2024440'], ['MUC_I2024450'], ['MUC_I2024460'], ['MUC_I2024470'], ['MUC_I2024480'], ['MUC_I2024490'], ['MUC_I202450'], ['MUC_I2024500'], ['MUC_I2024510'], ['MUC_I2024520'], ['MUC_I202460'], ['MUC_I202470'], ['MUC_I202480'], ['MUC_I202490'], ['MUC_I202510']]









        # print("node.name pSi", node.name, pSi)
        # print("len(pSi) = ", len(pSi))

        # Sのリストをself.psi4demand[w][0].extend(pSi[w])
        node.set_S2psi(pSi)


        #@241124 probe psi4demand[][]
        print("241124 probe psi4demand[][]", node.psi4demand)


        # memo for animation
        # ココで、Sの初期セット状態とbackward shiftをanimationすると分りやすい
        # Sをセットしたら一旦、外に出て、Sの初期状態を表示すると動きが分かる
        # Sのbackward LD shiftを別途、処理する。

        # shifting S2P
        # shiftS2P_LV()は"lead time"と"安全在庫"のtime shift
        node.calcS2P()  # backward plan with postordering


    else:

        # 物流をnodeとして定義する場合は、メソッド修正get_set_childrenP2S2psi

        # logistic_LT shiftしたPをセットしてからgathering
        # 親nodeを見てlogistic_LT_shiftでP2Sを.extend(lots)すればgathering不要

        # ココは、calc_bw_psi処理として外出しする

        # gathering S and Setting S
        node.get_set_childrenP2S2psi(node.plan_range)

        # shifting S2P
        # shiftS2P_LV()は"lead time"と"安全在庫"のtime shift
        node.calcS2P()  # backward plan with postordering










def set_psi_lists_postorder(node, node_psi_dict):

    for child in node.children:

        set_psi_lists_postorder(child, node_psi_dict)

    # キーが存在する場合は対応する値valueが返り、存在しない場合はNoneが返る。
    if node.children == []:  # 子nodeがないleaf nodeの場合

        # 辞書のgetメソッドでキーから値を取得。キーが存在しない場合はNone
        node.set_psi_list(node_psi_dict.get(node.name))

        # shifting S2P
        node.calcS2P()  # backward plan with postordering

    else:

        # gathering S and Setting S
        node.get_set_childrenP2S2psi(node.plan_range)
        # node.get_set_childrenS2psi(plan_range)

        # shifting S2P
        node.calcS2P()  # backward plan with postordering



# 同一node内のS2Pの処理
def shiftS2P_LV(psiS, shift_week, lv_week):  # LV:long vacations

    # ss = safety_stock_week
    sw = shift_week

    plan_len = len(psiS) - 1  # -1 for week list position

    for w in range(plan_len, sw, -1):  # backward planningで需要を降順でシフト

        # my_list = [1, 2, 3, 4, 5]
        # for i in range(2, len(my_list)):
        #    my_list[i] = my_list[i-1] + my_list[i-2]

        # 0:S
        # 1:CO
        # 2:I
        # 3:P

        eta_plan = w - sw  # sw:shift week (includung safty stock)

        eta_shift = check_lv_week_bw(lv_week, eta_plan)  # ETA:Estimate Time Arrival

        # リスト追加 extend
        # 安全在庫とカレンダ制約を考慮した着荷予定週Pに、w週Sからoffsetする

        psiS[eta_shift][3].extend(psiS[w][0])  # P made by shifting S with

    return psiS



# ************************************
# checking constraint to inactive week , that is "Long Vacation"
# ************************************
def check_lv_week_bw(const_lst, check_week):

    num = check_week

    if const_lst == []:

        pass

    else:

        while num in const_lst:

            num -= 1

    return num


def check_lv_week_fw(const_lst, check_week):

    num = check_week

    if const_lst == []:

        pass

    else:

        while num in const_lst:

            num += 1

    return num







# ****************************
# after demand leveling / planning outbound supply
# ****************************
def shiftS2P_LV_replace(psiS, shift_week, lv_week):  # LV:long vacations

    # ss = safety_stock_week
    sw = shift_week

    plan_len = len(psiS) - 1  # -1 for week list position

    for w in range(plan_len):  # foreward planningでsupplyのp [w][3]を初期化

        # psiS[w][0] = [] # S active

        psiS[w][1] = []  # CO
        psiS[w][2] = []  # I
        psiS[w][3] = []  # P

    for w in range(plan_len, sw, -1):  # backward planningでsupplyを降順でシフト

        # my_list = [1, 2, 3, 4, 5]
        # for i in range(2, len(my_list)):
        #    my_list[i] = my_list[i-1] + my_list[i-2]

        # 0:S
        # 1:CO
        # 2:I
        # 3:P

        eta_plan = w - sw  # sw:shift week ( including safty stock )

        eta_shift = check_lv_week_bw(lv_week, eta_plan)  # ETA:Eatimate Time Arrival

        # リスト追加 extend
        # 安全在庫とカレンダ制約を考慮した着荷予定週Pに、w週Sからoffsetする
        psiS[eta_shift][3].extend(psiS[w][0])  # P made by shifting S with

    return psiS




# *******************
# 生産平準化の前処理　ロット・カウント
# *******************
def count_lots_yyyy(psi_list, yyyy_str):

    matrix = psi_list

    # 共通の文字列をカウントするための変数を初期化
    count_common_string = 0

    # Step 1: マトリクス内の各要素の文字列をループで調べる
    for row in matrix:

        for element in row:

            # Step 2: 各要素内の文字列が "2023" を含むかどうかを判定
            if yyyy_str in element:

                # Step 3: 含む場合はカウンターを増やす
                count_common_string += 1

    return count_common_string


def is_52_or_53_week_year(year):
    # 指定された年の12月31日を取得
    last_day_of_year = dt.date(year, 12, 31)

    # 12月31日のISO週番号を取得 (isocalendar()メソッドはタプルで[ISO年, ISO週番号, ISO曜日]を返す)
    _, iso_week, _ = last_day_of_year.isocalendar()

    # ISO週番号が1の場合は前年の最後の週なので、52週と判定
    if iso_week == 1:
        return 52
    else:
        return iso_week


def find_depth(node):
    if not node.parent:
        return 0
    else:
        return find_depth(node.parent) + 1


def find_all_leaves(node, leaves, depth=0):
    if not node.children:
        leaves.append((node, depth))  # (leafノード, 深さ) のタプルを追加
    else:
        for child in node.children:
            find_all_leaves(child, leaves, depth + 1)


def make_nodes_decouple_all(node):

    #
    #    root_node = build_tree()
    #    set_parent(root_node)

    #    leaves = []
    #    find_all_leaves(root_node, leaves)
    #    pickup_list = leaves[::-1]  # 階層の深い順に並べる

    leaves = []
    leaves_name = []

    nodes_decouple = []

    find_all_leaves(node, leaves)
    # find_all_leaves(root_node, leaves)
    pickup_list = sorted(leaves, key=lambda x: x[1], reverse=True)
    pickup_list = [leaf[0] for leaf in pickup_list]  # 深さ情報を取り除く

    # こうすることで、leaf nodeを階層の深い順に並べ替えた pickup_list が得られます。
    # 先に深さ情報を含めて並べ替え、最後に深さ情報を取り除くという流れになります。

    # 初期処理として、pickup_listをnodes_decoupleにcopy
    # pickup_listは使いまわしで、pop / insert or append / removeを繰り返す
    for nd in pickup_list:
        nodes_decouple.append(nd.name)

    nodes_decouple_all = []

    while len(pickup_list) > 0:

        # listのcopyを要素として追加
        nodes_decouple_all.append(nodes_decouple.copy())

        current_node = pickup_list.pop(0)
        del nodes_decouple[0]  # 並走するnode.nameの処理

        parent_node = current_node.parent

        if parent_node is None:
            break

        # 親ノードをpick up対象としてpickup_listに追加
        if current_node.parent:

            #    pickup_list.append(current_node.parent)
            #    nodes_decouple.append(current_node.parent.name)

            # if parent_node not in pickup_list:  # 重複追加を防ぐ

            # 親ノードの深さを見て、ソート順にpickup_listに追加
            depth = find_depth(parent_node)
            inserted = False

            for idx, node in enumerate(pickup_list):

                if find_depth(node) <= depth:

                    pickup_list.insert(idx, parent_node)
                    nodes_decouple.insert(idx, parent_node.name)

                    inserted = True
                    break

            if not inserted:
                pickup_list.append(parent_node)
                nodes_decouple.append(parent_node.name)

            # 親ノードから見た子ノードをpickup_listから削除
            for child in parent_node.children:

                if child in pickup_list:

                    pickup_list.remove(child)
                    nodes_decouple.remove(child.name)

        else:

            print("error: node dupplicated", parent_node.name)

    return nodes_decouple_all



    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # Mother Plant demand leveling 
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def demand_leveling_on_ship(root_node_outbound, pre_prod_week, year_st, year_end):

    # input: root_node_outbound.psi4demand
    #        pre_prod_week =26 
    #
    # output:root_node_outbound.psi4supply







    plan_range = root_node_outbound.plan_range



    #@241114
    # 需給バランスの問題は、ひとつ上のネットワーク全体のoptimizeで解く

    # ロット単位で供給を変化させて、weight=ロット(CPU_profit)利益でsimulate
    # 設備投資の回収期間を見る

    # 供給>=需要ならオペレーション問題
    # 供給<需要なら供給配分とオペレーション問題

    # optimiseで、ルートと量を決定
    # PSIで、operation revenue cost profitを算定 business 評価

    # 業界No1/2/3の供給戦略をsimulateして、business評価する


    #@241114
    # ********************************
    # 先行生産の処理を見通しを良く書き直す
    # ********************************





    #@241113 STOP 初期セットで定義済み
    ## *********************************
    ## initial setting
    ## *********************************
    #node_psi_dict_Ot4Sp = {}  # node_psi_dict_Ot4Spの初期セット
    #
    #node_psi_dict_Ot4Sp = make_psi4supply(root_node_outbound, node_psi_dict_Ot4Sp)

    #
    # node_psi_dict_Ot4Dmでは、末端市場のleafnodeのみセット
    #
    # root_nodeのS psi_list[w][0]に、levelingされた確定出荷S_confirm_listをセッ    ト

    # 年間の総需要(総lots)をN週先行で生産する。
    # 例えば、３ヶ月先行は13週先行生産として、年間総需要を週平均にする。

    # S出荷で平準化して、confirmedS-I-P
    # conf_Sからconf_Pを生成して、conf_P-S-I  PUSH and PULL

    S_list = []
    S_allocated = []

    year_lots_list = []
    year_week_list = []

    leveling_S_in = []

    leveling_S_in = root_node_outbound.psi4demand

    # psi_listからS_listを生成する
    for psi in leveling_S_in:

        S_list.append(psi[0])

    # 開始年を取得する
    plan_year_st = year_st  # 開始年のセット in main()要修正

    for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):

        year_lots = count_lots_yyyy(S_list, str(yyyy))

        year_lots_list.append(year_lots)

    #        # 結果を出力
    #       #print(yyyy, " year carrying lots:", year_lots)
    #
    #    # 結果を出力
    #   #print(" year_lots_list:", year_lots_list)

    # an image of sample data
    #
    # 2023  year carrying lots: 0
    # 2024  year carrying lots: 2919
    # 2025  year carrying lots: 2914
    # 2026  year carrying lots: 2986
    # 2027  year carrying lots: 2942
    # 2028  year carrying lots: 2913
    # 2029  year carrying lots: 0
    #
    # year_lots_list: [0, 2919, 2914, 2986, 2942, 2913, 0]

    year_list = []

    for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):

        year_list.append(yyyy)

        # テスト用の年を指定
        year_to_check = yyyy

        # 指定された年のISO週数を取得
        week_count = is_52_or_53_week_year(year_to_check)

        year_week_list.append(week_count)

    #        # 結果を出力
    #       #print(year_to_check, " year has week_count:", week_count)
    #
    #    # 結果を出力
    #   #print(" year_week_list:", year_week_list)

    # print("year_list", year_list)

    # an image of sample data
    #
    # 2023  year has week_count: 52
    # 2024  year has week_count: 52
    # 2025  year has week_count: 52
    # 2026  year has week_count: 53
    # 2027  year has week_count: 52
    # 2028  year has week_count: 52
    # 2029  year has week_count: 52
    # year_week_list: [52, 52, 52, 53, 52, 52, 52]


    # *****************************
    # 生産平準化のための年間の週平均生産量(ロット数単位)
    # *****************************

    # *****************************
    # make_year_average_lots
    # *****************************
    # year_list     = [2023,2024,2025,2026,2027,2028,2029]

    # year_lots_list = [0, 2919, 2914, 2986, 2942, 2913, 0]
    # year_week_list = [52, 52, 52, 53, 52, 52, 52]

    year_average_lots_list = []

    for lots, weeks in zip(year_lots_list, year_week_list):

        average_lots_per_week = math.ceil(lots / weeks)

        year_average_lots_list.append(average_lots_per_week)


    # print("year_average_lots_list", year_average_lots_list)
    #
    # an image of sample data
    #
    # year_average_lots_list [0, 57, 57, 57, 57, 57, 0]

    # 年間の総需要(総lots)をN週先行で生産する。
    # 例えば、３ヶ月先行は13週先行生産として、年間総需要を週平均にする。

    #
    # 入力データの前提
    #
    # leveling_S_in[w][0] == S_listは、outboundのdemand_planで、
    # マザープラントの出荷ポジションのSで、
    # 5年分 週次 最終市場におけるlot_idリストが
    # LT offsetされた状態で入っている
    #
    # year_list     = [2023,2024,2025,2026,2027,2028,2029]

    # year_lots_list = [0, 2919, 2914, 2986, 2942, 2913, 0]
    # year_week_list = [52, 52, 52, 53, 52, 52, 52]
    # year_average_lots_list [0, 57, 57, 57, 57, 57, 0]

    # ********************************
    # 先行生産の週数
    # ********************************
    # precedence_production_week =13

    pre_prod_week =26 # 26週=6か月の先行生産をセット
    # pre_prod_week =13 # 13週=3か月の先行生産をセット
    # pre_prod_week = 6  # 6週=1.5か月の先行生産をセット

    # ********************************
    # 先行生産の開始週を求める
    # ********************************
    # 市場投入の前年において i= 0  year_list[i]           # 2023
    # 市場投入の前年のISO週の数 year_week_list[i]         # 52

    # 先行生産の開始週は、市場投入の前年のISO週の数 - 先行生産週

    pre_prod_start_week = 0

    i = 0

    pre_prod_start_week = year_week_list[i] - pre_prod_week

    # スタート週の前週まで、[]リストで埋めておく
    for i in range(pre_prod_start_week):
        S_allocated.append([])

    # ********************************
    # 最終市場からのLT offsetされた出荷要求lot_idリストを
    # Allocate demand to mother plant weekly slots
    # ********************************

    # S_listの週別lot_idリストを一直線のlot_idリストに変換する
    # mother plant weekly slots

    # 空リストを無視して、一直線のlot_idリストに変換

    # 空リストを除外して一つのリストに結合する処理
    S_one_list = [item for sublist in S_list if sublist for item in sublist]

    ## 結果表示
    ##print(S_one_list)

    # to be defined 毎年の定数でのlot_idの切り出し

    # listBの各要素で指定された数だけlistAから要素を切り出して
    # 新しいリストlistCを作成

    listA = S_one_list  # 5年分のlot_idリスト

    listB = year_lots_list  # 毎年毎の総ロット数

    listC = []  # 毎年のlot_idリスト

    start_idx = 0

    for i, num in enumerate(listB):

        end_idx = start_idx + num

        # original sample
        # listC.append(listA[start_idx:end_idx])

        # **********************************
        # "slice" and "allocate" at once
        # **********************************
        sliced_lots = listA[start_idx:end_idx]

        # 毎週の生産枠は、year_average_lots_listの平均値を取得する。
        N = year_average_lots_list[i]

        if N == 0:

            pass

        else:

            # その年の週次の出荷予定数が生成される。
            S_alloc_a_year = [
                sliced_lots[j : j + N] for j in range(0, len(sliced_lots), N)
            ]

            S_allocated.extend(S_alloc_a_year)
            # S_allocated.append(S_alloc_a_year)

        start_idx = end_idx

    ## 結果表示
    # print("S_allocated", S_allocated)

    # set psi on outbound supply

    # "JPN-OUT"
    #


    # ***********************************************
    #@241113 CHANGE root_node_outbound.psi4supplyが存在するという前提
    # ***********************************************
    #
    #node_name = root_node_outbound.name  # Nodeからnode_nameを取出す
    #
    ## for w, pSi in enumerate( S_allocated ):
    ##
    ##    node_psi_dict_Ot4Sp[node_name][w][0] = pSi
    
    for w in range(53 * plan_range):

        if w <= len(S_allocated) - 1:  # index=0 start

            root_node_outbound.psi4supply[w][0] = S_allocated[w]
            #node_psi_dict_Ot4Sp[node_name][w][0] = S_allocated[w]

        else:

            root_node_outbound.psi4supply[w][0] = []
            #node_psi_dict_Ot4Sp[node_name][w][0] = []


    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$





def place_P_in_supply_LT(w, child, lot):  # lot LT_shift on P

    # *******************************************
    # supply_plan上で、PfixをSfixにPISでLT offsetする
    # *******************************************

    # **************************
    # Safety Stock as LT shift
    # **************************

    #@240925 STOP
    ## leadtimeとsafety_stock_weekは、ここでは同じ
    ## safety_stock_week = child.leadtime
    #LT_SS_week = child.leadtime


    #@240925 長期休暇がLT_SS_weekかchild.leadtimeかどちらにある場合は???

    #@240925
    # leadtimeとsafety_stock_weekは別もの
    LT_SS_week   = child.safety_stock_week
    LT_logi_week = child.leadtime



    # **************************
    # long vacation weeks
    # **************************
    lv_week = child.long_vacation_weeks

    ## P to S の計算処理
    # self.psi4supply = shiftP2S_LV(self.psi4supply, safety_stock_week, lv_week)

    ### S to P の計算処理
    ##self.psi4demand = shiftS2P_LV(self.psi4demand, safety_stock_week, lv_week)

    # my_list = [1, 2, 3, 4, 5]
    # for i in range(2, len(my_list)):
    #    my_list[i] = my_list[i-1] + my_list[i-2]

    # 0:S
    # 1:CO
    # 2:I
    # 3:P


    #@240925 STOP
    ## LT:leadtime SS:safty stockは1つ
    ## foreward planで、「親confirmed_S出荷=子confirmed_P着荷」と表現
    #eta_plan = w + LT_SS_week  # ETA=ETDなので、+LTすると次のETAとなる


    # LT_logi_weekで子nodeまでの物流LTを考慮
    eta_plan = w + LT_logi_week


    # etd_plan = w + ss # ss:safty stock
    # eta_plan = w - ss # ss:safty stock

    # *********************
    # 着荷週が事業所nodeの非稼働週の場合 +1次週の着荷とする
    # *********************
    # 着荷週を調整
    eta_shift = check_lv_week_fw(lv_week, eta_plan)  # ETA:Eatimate Time Arriv

    # リスト追加 extend
    # 安全在庫とカレンダ制約を考慮した着荷予定週Pに、w週Sからoffsetする

    # lot by lot operation
    # confirmed_P made by shifting parent_conf_S

    # ***********************
    # place_lot_supply_plan
    # ***********************

    # ここは、"REPLACE lot"するので、appendの前にchild psiをzero clearしてから

    #@240925 STOP
    ## 今回のmodelでは、輸送工程もpsi nodeと同等に扱っている(=POではない)ので
    ## 親のconfSを「そのままのWで」子のconfPに置く place_lotする
    #child.psi4supply[w][3].append(lot)

    ## 親のconfSを「eta_shiftしたWで」子のconfPに置く place_lotする
    # 親のconfSを「LT=輸送LT + 加工LT + SSでwをshiftして」子confSにplace_lot

    child.psi4supply[eta_shift][3].append(lot)

    # print("len(child.psi4supply)", len(child.psi4supply) ) # len() of psi list    # print("lot child.name eta_shift ",lot,  child.name, eta_shift )  # LT shift weeks


    # Sは、SS在庫分の後に出荷する
    ship_position = eta_shift + LT_SS_week

    # 出荷週を調整
    ship_shift = check_lv_week_fw(lv_week, ship_position) 

    child.psi4supply[ship_shift][0].append(lot)




def find_path_to_leaf_with_parent(node, leaf_node, current_path=[]):

    current_path.append(leaf_node.name)

    if node.name == leaf_node.name:

        return current_path

    else:

        parent = leaf_node.parent

        path = find_path_to_leaf_with_parent(node, parent, current_path.copy())

    return path


#        if path:
#
#            return path



def extract_node_name(stringA):
    # 右側の数字部分を除外してnode名を取得

    index = len(stringA) - 1

    while index >= 0 and stringA[index].isdigit():

        index -= 1

    node_name = stringA[: index + 1]

    return node_name




# ******************************************
# confirmedSを出荷先ship2のPとSにshift&set
# ******************************************
def feedback_psi_lists(node, nodes):
#def feedback_psi_lists(node, node_psi_dict, nodes):

    # キーが存在する場合は対応する値valueが返り、存在しない場合はNoneが返る。

    if node.children == []:  # 子nodeがないleaf nodeの場合

        pass

    else:

        # ************************************
        # clearing children P[w][3] and S[w][0]
        # ************************************
        # replace lotするために、事前に、
        # 出荷先となるすべてのchildren nodesのS[w][0]とP[w][3]をクリア

        for child in node.children:

            for w in range(53 * node.plan_range):

                child.psi4supply[w][0] = []
                child.psi4supply[w][3] = []

        # lotidから、leaf_nodeを特定し、出荷先ship2nodeに出荷することは、
        # すべての子nodeに出荷することになる

        # ************************************
        # setting mother_confirmed_S
        # ************************************
        # このnode内での子nodeへの展開
        for w in range(53 * node.plan_range):

            confirmed_S_lots = node.psi4supply[w][0]  # 親の確定出荷confS lot

            # 出荷先nodeを特定して

            # 一般には、下記のLT shiftだが・・・・・
            # 出荷先の ETA = LT_shift(ETD) でP place_lot
            # 工程中の ETA = SS_shift(ETD) でS place_lot

            # 本モデルでは、輸送工程 = modal_nodeを想定して・・・・・
            # 出荷先の ETA = 出荷元ETD        でP place_lot
            # 工程中の ETA = LT&SS_shift(ETD) でS place_lot
            # というイビツなモデル定義・・・・・

            # 直感的なPO=INVOICEという考え方に戻すべきかも・・・・・
            #
            # modal shiftのmodelingをLT_shiftとの拡張で考える???
            # modal = BOAT/AIR/QURIE
            # LT_shift(modal, w, ,,,,

            for lot in confirmed_S_lots:

                if lot == []:

                    pass

                else:

                    # *********************************************************
                    # child#ship2node = find_node_to_ship(node, lot)
                    # lotidからleaf_nodeのpointerを返す
                    leaf_node_name = extract_node_name(lot)

                    leaf_node = nodes[leaf_node_name]

                    # 末端からあるnodeAまでleaf_nodeまでのnode_listをpathで返す

                    current_path = []
                    path = []

                    path = find_path_to_leaf_with_parent(node, leaf_node, current_path)

                    # nodes_listを逆にひっくり返す
                    path.reverse()

                    # 出荷先nodeはnodeAの次node、path[1]になる
                    ship2node_name = path[1]

                    ship2node = nodes[ship2node_name]

                    # ここでsupply planを更新している
                    # 出荷先nodeのPSIのPとSに、confirmed_S中のlotをby lotで置く
                    #place_P_in_supply(w, ship2node, lot)
                    place_P_in_supply_LT(w, ship2node, lot)

    for child in node.children:

        feedback_psi_lists(child, nodes)
        #feedback_psi_lists(child, node_psi_dict, nodes)






def copy_S_demand2supply(node): # TOBE 240926
#def update_child_PS(node): # TOBE 240926

    # 明示的に.copyする。
    plan_len = 53 * node.plan_range
    for w in range(0, plan_len):

        node.psi4supply[w][0] = node.psi4demand[w][0].copy()


def PUSH_process(node):


    # ***************
    # decoupl nodeに入って最初にcalcPS2Iで状態を整える
    # ***************
    node.calcPS2I4supply()  # calc_psi with PULL_S


    # STOP STOP
    ##@241002 decoupling nodeのみpullSで確定ship
    ## *******************************************
    ## decouple nodeは、pull_Sで出荷指示する
    ## *******************************************
    ## copy S demand2supply
    #copy_S_demand2supply(node)
    #
    ## 自分のnodeをPS2Iで確定する
    #node.calcPS2I4supply()  # calc_psi with PUSH_S


    print(f"PUSH_process applied to {node.name}")



def copy_P_demand2supply(node): # TOBE 240926
#def update_child_PS(node): # TOBE 240926

    # 明示的に.copyする。
    plan_len = 53 * node.plan_range
    for w in range(0, plan_len):

        node.psi4supply[w][3] = node.psi4demand[w][3].copy()



def PULL_process(node):
    # *******************************************
    # decouple nodeは、pull_Sで出荷指示する
    # *******************************************

    #@241002 childで、親nodeの確定S=確定P=demandのPで計算済み
    # copy S&P demand2supply for PULL
    copy_S_demand2supply(node)
    copy_P_demand2supply(node)


    # 自分のnodeをPS2Iで確定する
    node.calcPS2I4supply()  # calc_psi with PULL_S&P

    print(f"PULL_process applied to {node.name}")



def apply_pull_process(node):

    #@241002 MOVE
    #PULL_process(node)

    for child in node.children:


        PULL_process(child)


        apply_pull_process(child)




def push_pull_all_psi2i_decouple4supply5(node, decouple_nodes):

    if node.name in decouple_nodes:

        # ***************
        # decoupl nodeに入って最初にcalcPS2Iで状態を整える
        # ***************
        node.calcPS2I4supply()  # calc_psi with PULL_S


        #@241002 decoupling nodeのみpullSで確定ship
        # *******************************************
        # decouple nodeは、pull_Sで出荷指示する
        # *******************************************
        copy_S_demand2supply(node)

        PUSH_process(node)         # supply SP2Iしてからの

        apply_pull_process(node)   # demandSに切り替え

    else:

        PUSH_process(node)

        for child in node.children:

            push_pull_all_psi2i_decouple4supply5(child, decouple_nodes)




# ****************************
# evaluation plan
# ****************************



def eval_supply_chain(node):

    # *********************
    # counting Purchase Order
    # *********************
    # psi_listのPOは、psi_list[w][3]の中のlot_idのロット数=リスト長
    node.set_lot_counts()





    # *********************
    # EvalPlanSIP()の中でnode instanceに以下をセットする
    # self.profit, self.revenue, self.profit_ratio
    # *********************

    # ここでは、by weekの計画状態xxx[w]の変化を評価して、self.eval_xxxにセット
    node.EvalPlanSIP()

    # print(
    #    "Eval node profit revenue profit_ratio",
    #    node.name,
    #    node.eval_profit,
    #    node.eval_revenue,
    #    node.eval_profit_ratio,
    # )

    for child in node.children:

        eval_supply_chain(child)






# ****************************
# Definition END of PySI module
# ****************************



# ****************************
# Definition START of Viewer
# ****************************



def tune_hammock(pos_E2E):
    # Compare 'procurement_office' and 'sales_office' Y values and choose the larger one
    procurement_office_y = pos_E2E['procurement_office'][1]
    office_y = pos_E2E['sales_office'][1]

    max_y = max(procurement_office_y, office_y)
    
    pos_E2E['procurement_office'] = (pos_E2E['procurement_office'][0], max_y)
    pos_E2E['sales_office'] = (pos_E2E['sales_office'][0], max_y)

    # Align 'FA_xxxx' and 'PL_xxxx' pairs
    for key, value in pos_E2E.items():
        if key.startswith('FA_'):
            corresponding_key = 'PL_' + key[3:]
            if corresponding_key in pos_E2E:
                fa_y = value[1]
                pl_y = pos_E2E[corresponding_key][1]
                aligned_y = max(fa_y, pl_y)
                pos_E2E[key] = (value[0], aligned_y)
                pos_E2E[corresponding_key] = (pos_E2E[corresponding_key][0], aligned_y)

    return pos_E2E




# **** an image ****
#pos_office {'JPN': (0, 5.55), 'HAM': (1, 2.2), 'HAM_N': (2, 0.0), 'HAM_D': (2, 1.2000000000000002), 'HAM_I': (2, 2.4000000000000004), 'MUC': (2, 1.6000000000000003), 'MUC_N': (3, 0.0), 'MUC_D': (3, 1.4000000000000004), 'MUC_I': (3, 2.8000000000000007), 'FRALEAF': (2, 4.800000000000001), 'SHA': (1, 6.199999999999999), 'SHA_N': (2, 5.0), 'SHA_D': (2, 6.199999999999999), 'SHA_I': (2, 7.4), 'CAN': (1, 9.299999999999999), 'CAN_N': (2, 8.0), 'CAN_D': (2, 9.2), 'CAN_I': (2, 10.399999999999999)}










# ***************************
# make network with NetworkX
# show network with plotly
# ***************************



def calc_put_office_position(pos_office, office_name):
    x_values = [pos_office[key][0] for key in pos_office]
    max_x = max(x_values)
    y_values = [pos_office[key][1] for key in pos_office]
    max_y = max(y_values)
    pos_office[office_name] = (max_x + 1, max_y + 1)
    return pos_office

def generate_positions(node, pos, depth=0, y_offset=0, leaf_y_positions=None):
    if not node.children:
        pos[node.name] = (depth, leaf_y_positions.pop(0))
    else:
        child_y_positions = []
        for child in node.children:
            generate_positions(child, pos, depth + 1, y_offset, leaf_y_positions)
            child_y_positions.append(pos[child.name][1])
        pos[node.name] = (depth, sum(child_y_positions) / len(child_y_positions))  # 子ノードのY軸平均値を親ノードに設定
    return pos

def count_leaf_nodes(node):
    if not node.children:
        return 1
    return sum(count_leaf_nodes(child) for child in node.children)

def get_leaf_y_positions(node, y_positions=None):
    if y_positions is None:
        y_positions = []
    if not node.children:
        y_positions.append(len(y_positions))
    else:
        for child in node.children:
            get_leaf_y_positions(child, y_positions)
    return y_positions

def tune_hammock(pos_E2E, nodes_outbound, nodes_inbound):
    # Compare 'procurement_office' and 'sales_office' Y values and choose the larger one
    procurement_office_y = pos_E2E['procurement_office'][1]
    office_y = pos_E2E['sales_office'][1]

    max_y = max(procurement_office_y, office_y)
    
    pos_E2E['procurement_office'] = (pos_E2E['procurement_office'][0], max_y)
    pos_E2E['sales_office'] = (pos_E2E['sales_office'][0], max_y)

    # Align 'FA_xxxx' and 'PL_xxxx' pairs and their children
    for key, value in pos_E2E.items():
        if key.startswith('MOM'):
            corresponding_key = 'DAD' + key[3:]
            if corresponding_key in pos_E2E:
                fa_y = value[1]
                pl_y = pos_E2E[corresponding_key][1]
                aligned_y = max(fa_y, pl_y)
                pos_E2E[key] = (value[0], aligned_y)
                pos_E2E[corresponding_key] = (pos_E2E[corresponding_key][0], aligned_y)


                offset_y = max( aligned_y - fa_y, aligned_y - pl_y )

                if aligned_y - fa_y == 0: # inboundの高さが同じ outboundを調整
                    
                    pool_node = nodes_outbound[corresponding_key]
                    adjust_child_positions(pool_node, pos_E2E, offset_y)

                else:

                    fassy_node = nodes_inbound[key]
                    adjust_child_positions(fassy_node, pos_E2E, offset_y)



                ## Adjust children nodes
                #adjust_child_positions(pos_E2E, key, aligned_y)
                #adjust_child_positions(pos_E2E, corresponding_key, aligned_y)

    return pos_E2E

#def adjust_child_positions(pos, parent_key, parent_y):
#    for key, value in pos.items():
#        if key != parent_key and pos[key][0] > pos[parent_key][0]:
#            pos[key] = (value[0], value[1] + (parent_y - pos[parent_key][1]))


def adjust_child_positions(node, pos, offset_y):
    if node.children == []:  # leaf_nodeを判定
        pass
    else:
        for child in node.children:
            # yの高さを調整 
            pos[child.name] = (pos[child.name][0], pos[child.name][1]+offset_y)
            adjust_child_positions(child, pos, offset_y)


def make_E2E_positions(root_node_outbound, root_node_inbound):
    out_leaf_count = count_leaf_nodes(root_node_outbound)
    in_leaf_count = count_leaf_nodes(root_node_inbound)

    print("out_leaf_count", out_leaf_count)
    print("in_leaf_count", in_leaf_count)

    out_leaf_y_positions = get_leaf_y_positions(root_node_outbound)
    in_leaf_y_positions = get_leaf_y_positions(root_node_inbound)

    pos_out = generate_positions(root_node_outbound, {}, leaf_y_positions=out_leaf_y_positions)
    pos_out = calc_put_office_position(pos_out, "sales_office")

    pos_in = generate_positions(root_node_inbound, {}, leaf_y_positions=in_leaf_y_positions)
    pos_in = calc_put_office_position(pos_in, "procurement_office")

    max_x = max(x for x, y in pos_in.values())
    pos_in_reverse = {node: (max_x - x, y) for node, (x, y) in pos_in.items()}
    pos_out_shifting = {node: (x + max_x, y) for node, (x, y) in pos_out.items()}

    merged_dict = pos_in_reverse.copy()
    for key, value in pos_out_shifting.items():
        if key in merged_dict:
            if key == root_node_outbound.name:
                merged_dict[key] = value if value[1] > merged_dict[key][1] else merged_dict[key]
            else:
                merged_dict[key] = value
        else:
            merged_dict[key] = value

    pos_E2E = merged_dict

    return pos_E2E




def Gsp_add_edge_sc2nx_inbound(node, Gsp):

    if node.children == []:  # leaf_nodeを判定

        # ******************************
        # capacity4nx = average demand lots # ave weekly demand をそのままset
        # ******************************
        capacity4nx = 0
        demand_lots = 0
        ave_demand_lots = 0

        for w in range(53 * node.plan_range):
            demand_lots += len(node.psi4demand[w][0])

        ave_demand_lots = demand_lots / (53 * node.plan_range)

        capacity4nx = ave_demand_lots  # N * ave weekly demand

        # ******************************
        # edge connecting leaf_node and "sales_office" 接続
        # ******************************

        # float2int
        capacity4nx_int = float2int(capacity4nx)

        Gsp.add_edge( "procurement_office", node.name,
                 weight=0,
                 capacity = 2000 # 240906 TEST # capacity4nx_int * 1 # N倍
                 #capacity=capacity4nx_int * 1 # N倍
        )

        # pass

    else:

        for child in node.children:

            # *****************************
            # make_edge_weight_capacity
            # *****************************
            weight4nx, capacity4nx = make_edge_weight_capacity(node, child)

            # float2int
            weight4nx_int = float2int(weight4nx)
            capacity4nx_int = float2int(capacity4nx)

            #@240906 TEST 
            capacity4nx_int = 2000

            child.nx_weight = weight4nx_int
            child.nx_capacity = capacity4nx_int

            # ******************************
            # edge connecting self.node & child.node
            # ******************************

            Gsp.add_edge(
                child.name, node.name, 
                weight=weight4nx_int,

                capacity=capacity4nx_int
            )

            Gsp_add_edge_sc2nx_inbound(child, Gsp)



def Gdm_add_edge_sc2nx_outbound(node, Gdm):

    if node.children == []:  # leaf_nodeを判定

        # ******************************
        # capacity4nx = average demand lots # ave weekly demand をそのままset
        # ******************************
        capacity4nx = 0
        demand_lots = 0
        ave_demand_lots = 0

        for w in range(53 * node.plan_range):
            demand_lots += len(node.psi4demand[w][0])



        ave_demand_lots = demand_lots / (53 * node.plan_range)

        #@ STOP
        #capacity4nx = ave_demand_lots  # N * ave weekly demand

        tariff_portion = node.tariff_on_price / node.cs_price_sales_shipped

        demand_on_curve = 3 * ave_demand_lots * (1- tariff_portion) * node.price_elasticity 


        print("node.name", node.name)

        print("node.tariff_on_price", node.tariff_on_price)
        print("node.cs_price_sales_shipped", node.cs_price_sales_shipped)
        print("tariff_portion", tariff_portion)

        print("ave_demand_lots", ave_demand_lots)
        print("node.price_elasticity", node.price_elasticity)
        print("demand_on_curve", demand_on_curve)



        #demand_on_curve = 3 * ave_demand_lots * (1-(customs_tariff*0.5 / node.cs_price_sales_shipped) * node.price_elasticity )

        capacity4nx = demand_on_curve       # 


        print("capacity4nx", capacity4nx)



        # ******************************
        # edge connecting leaf_node and "sales_office" 接続
        # ******************************

        # float2int
        capacity4nx_int = float2int(capacity4nx)

        # set PROFIT 2 WEIGHT

        Gdm.add_edge(node.name, "sales_office",
                 weight=0,
                 capacity=capacity4nx_int * 1 # N倍
        )

        print(
            "Gdm.add_edge(node.name, office",
            node.name,
            "sales_office",
            "weight = 0, capacity =",
            capacity4nx,
        )

        # pass

    else:

        for child in node.children:

            # *****************************
            # make_edge_weight_capacity
            # *****************************
            weight4nx, capacity4nx = make_edge_weight_capacity(node, child)

            # float2int
            weight4nx_int = float2int(weight4nx)
            capacity4nx_int = float2int(capacity4nx)

            child.nx_weight = weight4nx_int
            child.nx_capacity = capacity4nx_int

            # ******************************
            # edge connecting self.node & child.node
            # ******************************

            Gdm.add_edge(
                node.name, child.name, 
                weight=weight4nx_int,

                capacity=capacity4nx_int
            )

            print(
                "Gdm.add_edge(node.name, child.name",
                node.name, child.name,
                "weight =", weight4nx_int,
                "capacity =", capacity4nx_int
            )

            Gdm_add_edge_sc2nx_outbound(child, Gdm)






def make_edge_weight(node, child):


#NetworkXでは、エッジの重み（weight）が大きい場合、そのエッジの利用優先度は、アルゴリズムや目的によって異なる

    # Weight (重み)
    #    - `weight`はedgeで定義された2ノード間で発生するprofit(rev-cost)で表す
    #       cost=物流費、関税、保管コストなどの合計金額に対応する。
    #    - 例えば、物流費用が高い場合、対応するエッジの`weight`は低くなる。
    #     最短経路アルゴリズム(ダイクストラ法)を適用すると適切な経路を選択する。

#最短経路アルゴリズム（例：Dijkstra’s algorithm）では、エッジの重みが大きいほど、そのエッジを通る経路のコストが高くなるため、優先度は下がる

#最大フロー問題などの他のアルゴリズムでは、エッジの重みが大きいほど、そのエッジを通るフローが多くなるため、優先度が上がることがある
#具体的な状況や使用するアルゴリズムによって異なるため、
#目的に応じて適切なアルゴリズムを選択することが重要

# 最大フロー問題（Maximum Flow Problem）
# フォード・ファルカーソン法 (Ford-Fulkerson Algorithm)
#フォード・ファルカーソン法は、ネットワーク内のソース（始点）からシンク（終点）までの最大フローを見つけるアルゴリズム
#このアルゴリズムでは、エッジの重み（容量）が大きいほど、そのエッジを通るフローが多くなるため、優先度が上がります。


#@240831 
#    # *****************************************************
#    # 在庫保管コストの算定のためにevalを流す
#    # 子ノード child.
#    # *****************************************************
#
#    stock_cost = 0
#
#    child.EvalPlanSIP()
#
#    stock_cost = child.eval_WH_cost = sum(child.WH_cost[1:])
#
#    customs_tariff = 0
#    customs_tariff = child.customs_tariff_rate * child.REVENUE_RATIO  # 関税率 X 単価
#
#    # 物流コスト
#    # + TAX customs_tariff
#    # + 在庫保管コスト
#    # weight4nx = child.Distriburion_Cost + customs_tariff + stock_cost


    # priority is "profit"

    weight4nx = 0

    weight4nx = child.cs_profit_accume

    return weight4nx





#@240830 コこを修正
# 1.capacityの計算は、supply sideで製品ロット単位の統一したroot_capa * N倍
# 2.自node=>親nodeの関係定義 G.add_edge(self.node, parent.node)

def G_add_edge_from_inbound_tree(node, supplyers_capacity, G):

    if node.children == []:  # leaf_nodeを判定

        # ******************************
        # capacity4nx = average demand lots # ave weekly demand *N倍をset
        # ******************************
        capacity4nx = 0

        # 
        # ******************************
        #demand_lots = 0
        #ave_demand_lots = 0
        #
        #for w in range(53 * node.plan_range):
        #    demand_lots += len(node.psi4demand[w][0])
        #
        #ave_demand_lots = demand_lots / (53 * node.plan_range)
        #
        #capacity4nx = ave_demand_lots * 5  # N * ave weekly demand
        #
        # ******************************

        # supplyers_capacityは、root_node=mother plantのcapacity
        # 末端suppliersは、平均の5倍のcapa
        capacity4nx = supplyers_capacity * 5  # N * ave weekly demand


        # float2int
        capacity4nx_int = float2int(capacity4nx)

        # ******************************
        # edge connecting leaf_node and "procurement_office" 接続
        # ******************************

        G.add_edge("procurement_office", node.name, weight=0, capacity=2000)

        #G.add_edge("procurement_office", node.name, weight=0, capacity=capacity4nx_int)

        print(
            "G.add_edge(node.name, office",
            node.name,
            "sales_office",
            "weight = 0, capacity =",
            capacity4nx,
        )

        # pass

    else:

        for child in node.children:


            # supplyers_capacityは、root_node=mother plantのcapacity
            # 中間suppliersは、平均の3倍のcapa
            capacity4nx = supplyers_capacity * 3  # N * ave weekly demand


            # *****************************
            # set_edge_weight
            # *****************************
            weight4nx = make_edge_weight(node, child)

            ## *****************************
            ## make_edge_weight_capacity
            ## *****************************
            #weight4nx, capacity4nx = make_edge_weight_capacity(node, child)



            # float2int
            weight4nx_int = float2int(weight4nx)
            capacity4nx_int = float2int(capacity4nx)

            child.nx_weight = weight4nx_int
            child.nx_capacity = capacity4nx_int

            # ******************************
            # edge connecting from child.node to self.node as INBOUND
            # ******************************
            #G.add_edge(
            #    child.name, node.name, 
            #    weight=weight4nx_int, capacity=capacity4nx_int
            #)

            G.add_edge(
                child.name, node.name, 
                weight=weight4nx_int, capacity=2000
            )

            #print(
            #    "G.add_edge(child.name, node.name ",
            #    child.name,
            #    node.name,
            #    "weight =",
            #    weight4nx_int,
            #    "capacity =", 
            #    capacity4nx_int,
            #)

            G_add_edge_from_inbound_tree(child, supplyers_capacity, G)



def make_edge_weight_capacity(node, child):
    # Weight (重み)
    #    - `weight`は、edgeで定義された2つのノード間の移動コストを表す。
    #       物流費、関税、保管コストなどの合計金額に対応する。
    #    - 例えば、物流費用が高い場合、対応するエッジの`weight`は高くなる。
    #     最短経路アルゴリズム(ダイクストラ法)を適用すると適切な経路を選択する。
    #
    #    self.demandにセット?
    #

    # *********************
    # add_edge_parameter_set_weight_capacity()
    # add_edge()の前処理
    # *********************
    # capacity
    # - `capacity`は、エッジで定義された2つのノード間における期間当たりの移動量
    #   の制約を表します。
    # - サプライチェーンの場合、以下のアプリケーション制約条件を考慮して
    #   ネック条件となる最小値を設定する。
    #     - 期間内のノード間物流の容量の上限値
    #     - 通関の期間内処理量の上限値
    #     - 保管倉庫の上限値
    #     - 出庫・出荷作業の期間内処理量の上限値


    # *****************************************************
    # 在庫保管コストの算定のためにevalを流す
    # 子ノード child.
    # *****************************************************
    stock_cost = 0

    #@ 要確認
    #@241231 ココは新しいcost_tableで評価する
    child.EvalPlanSIP_cost()

    #@ OLD STOP
    #child.EvalPlanSIP()

    stock_cost = child.eval_WH_cost = sum(child.WH_cost[1:])

    customs_tariff = 0

    #@241231 関税率 X 仕入れ単価とする
    customs_tariff = child.customs_tariff_rate * child.cs_direct_materials_costs

    print("child.name", child.name)
    print("child.customs_tariff_rate", child.customs_tariff_rate)
    print("child.cs_direct_materials_costs", child.cs_direct_materials_costs)
    print("customs_tariff", customs_tariff)

    print("self.cs_price_sales_shipped", node.cs_price_sales_shipped)
    print("self.cs_cost_total", node.cs_cost_total)
    print("self.cs_profit", node.cs_profit)


    #関税コストの吸収方法 1
    # 1. 利益を維持し、コストと価格に上乗せする。
    # 2. 価格を維持し、コストに上乗せし、利益を削る。

    #    self.cs_price_sales_shipped # revenue
    #    self.cs_cost_total          # cost
    #    self.cs_profit              # profit


    #@ OLD STOP
    # 関税率 X 単価
    #customs_tariff = child.customs_tariff_rate * child.REVENUE_RATIO



    weight4nx = 0


    # 物流コスト
    # + TAX customs_tariff
    # + 在庫保管コスト
    # weight4nx = child.Distriburion_Cost + customs_tariff + stock_cost


    #@241231 仮定:関税の増分50%を利益削減する
    cost_portion = 0.5  # price_portion = 0.5 is following

    #@ RUN 
    weight4nx = child.cs_cost_total + (customs_tariff * cost_portion)



    #@ STOP
    #weight4nx = child.cs_profit_accume - (customs_tariff * cost_portion)
    #weight4nx =100*2 - child.cs_profit_accume + (customs_tariff *cost_portion)

    #print("child.cs_profit_accume", child.cs_profit_accume)

    print("child.cs_cost_total", child.cs_cost_total)

    print("customs_tariff", customs_tariff)
    print("cost_portion", cost_portion)
    print("weight4nx", weight4nx)



    if weight4nx < 0:
        weight4nx = 0


    # 出荷コストはPO_costに含まれている
    ## 出荷コスト
    # + xxxx

    #print("child.Distriburion_Cost", child.Distriburion_Cost)
    #print("+ TAX customs_tariff", customs_tariff)
    #print("+ stock_cost", stock_cost)
    #print("weight4nx", weight4nx)

    # ******************************
    # capacity4nx = 3 * average demand lots # ave weekly demand の3倍のcapa
    # ******************************
    capacity4nx = 0

    # ******************************
    # average demand lots
    # ******************************
    demand_lots = 0
    ave_demand_lots = 0

    for w in range(53 * node.plan_range):
        demand_lots += len(node.psi4demand[w][0])

    ave_demand_lots = demand_lots / (53 * node.plan_range)

    #@241231 仮定:関税の増分50%を価格増加による需要曲線上の価格弾力性=1とする
    # on the demand curve,
    # assume a price elasticity of demand of 1 due to price increase.

    #    self.cs_price_sales_shipped # revenue

    # demand_on_curve 需要曲線上の需要
    # customs_tariff*0.5 関税の50%
    # self.cs_price_sales_shipped 売上

    # 価格弾力性による需要変化
    # customs_tariff*0.5 / self.cs_price_sales_shipped 価格増加率
    # self.price_elasticity
    # 0.0: demand "stay" like a medecine
    # 1.0: demand_decrease = price_increse * 1
    # 2.0: demand_decrease = price_increse * 2

    #@241231 MEMO demand_curve
    # 本来、demandは価格上昇時に末端市場leaf_nodeで絞られるが、
    # ここでは、通関時の中間nodeのcapacityでdemandを絞ることで同様の効果とする

    # 末端価格ではないので、関税による価格増減率が異なる?
    # customs_tariff:関税増分のcostを退避しておく、self.customs_tariff
    # leaf_nodeの末端価格のdemand_on_curve = 価格増加率 * node.price_elasticity


    # (customs_tariff * 0.5) をlead_nodeのnode.tariff_on_priceにadd

    def add_tariff_on_leaf(node, customs_tariff):

        price_portion = 0.5 # cost_portion = 0.5 is previously defined

        if node.children == []:  # leaf_node
            node.tariff_on_price += customs_tariff * price_portion # 0.5
        else:
            for child in node.children:
                add_tariff_on_leaf(child, customs_tariff)

    add_tariff_on_leaf(node, customs_tariff)

    #@ STOP
    #demand_on_curve = 3 * ave_demand_lots * (1-(customs_tariff*0.5 / node.cs_price_sales_shipped) * node.price_elasticity )
    #
    #capacity4nx = demand_on_curve       # 


    #@ STOP RUN
    capacity4nx = 3 * ave_demand_lots  # N * ave weekly demand

    print("weight4nx", weight4nx)
    print("capacity4nx", capacity4nx)

    return weight4nx, capacity4nx  # ココはfloatのまま戻す




def G_add_edge_from_tree(node, G):

    if node.children == []:  # leaf_nodeを判定

        # ******************************
        # capacity4nx = average demand lots # ave weekly demand をそのままset
        # ******************************
        capacity4nx = 0
        demand_lots = 0
        ave_demand_lots = 0

        for w in range(53 * node.plan_range):
            demand_lots += len(node.psi4demand[w][0])

        ave_demand_lots = demand_lots / (53 * node.plan_range)

        capacity4nx = ave_demand_lots  # N * ave weekly demand


        # ******************************
        # edge connecting leaf_node and "sales_office" 接続
        # ******************************

        #@ RUN X1
        capacity4nx_int = round(capacity4nx) + 1

        #@ STOP
        # float2int X100
        #capacity4nx_int = float2int(capacity4nx)

        G.add_edge(node.name, "sales_office",
                 weight=0,
                 #capacity=capacity4nx_int
                 capacity=2000
        )

        print(
            "G.add_edge(node.name, office",
            node.name,
            "sales_office",
            "weight = 0, capacity =",
            capacity4nx,
        )

        # pass

    else:

        for child in node.children:

            # *****************************
            # make_edge_weight_capacity
            # *****************************
            weight4nx, capacity4nx = make_edge_weight_capacity(node, child)

            # float2int
            weight4nx_int = float2int(weight4nx)

            #@ RUN X1
            capacity4nx_int = round(capacity4nx) + 1

            #@ STOP
            # float2int X100
            #capacity4nx_int = float2int(capacity4nx)

            child.nx_weight = weight4nx_int
            child.nx_capacity = capacity4nx_int

            # ******************************
            # edge connecting self.node & child.node
            # ******************************

            G.add_edge(
                node.name, child.name, 
                weight=weight4nx_int,

                #capacity=capacity4nx_int
                capacity=2000

            )

            print(
                "G.add_edge(node.name, child.name",
                node.name,
                child.name,
                "weight =",
                weight4nx_int,
                "capacity =",
                capacity4nx_int,
            )

            G_add_edge_from_tree(child, G)




    # *********************
    # OUT treeを探索してG.add_nodeを処理する
    # node_nameをGにセット (X,Y)はfreeな状態、(X,Y)のsettingは後処理
    # *********************
def G_add_nodes_from_tree(node, G):


    G.add_node(node.name, demand=0)
    #G.add_node(node.name, demand=node.nx_demand) #demandは強い制約でNOT set!!

    print("G.add_node", node.name, "demand =", node.nx_demand)

    if node.children == []:  # leaf_nodeの場合、total_demandに加算

        pass

    else:

        for child in node.children:

            G_add_nodes_from_tree(child, G)



    # *********************
    # IN treeを探索してG.add_nodeを処理する。ただし、root_node_inboundをskip
    # node_nameをGにセット (X,Y)はfreeな状態、(X,Y)のsettingは後処理
    # *********************
def G_add_nodes_from_tree_skip_root(node, root_node_name_in, G):

    #@240901STOP
    #if node.name == root_node_name_in:
    #
    #    pass
    #
    #else:
    #
    #    G.add_node(node.name, demand=0)
    #    print("G.add_node", node.name, "demand = 0")

    G.add_node(node.name, demand=0)
    print("G.add_node", node.name, "demand = 0")

    if node.children == []:  # leaf_nodeの場合

        pass

    else:

        for child in node.children:

            G_add_nodes_from_tree_skip_root(child, root_node_name_in, G)
        






# *****************
# demand, weight and scaling FLOAT to INT
# *****************
def float2int(value):

    scale_factor = 100
    scaled_demand = value * scale_factor

    # 四捨五入
    rounded_demand = round(scaled_demand)
    # print(f"四捨五入: {rounded_demand}")

    ## 切り捨て
    # floored_demand = math.floor(scaled_demand)
    # print(f"切り捨て: {floored_demand}")

    ## 切り上げ
    # ceiled_demand = math.ceil(scaled_demand)
    # print(f"切り上げ: {ceiled_demand}")

    return rounded_demand


    # *********************
    # 末端市場、最終消費の販売チャネルのdemand = leaf_node_demand
    # treeのleaf nodesを探索して"weekly average base"のtotal_demandを集計
    # *********************
def set_leaf_demand(node, total_demand):

    if node.children == []:  # leaf_nodeの場合、total_demandに加算

        # ******************************
        # average demand lots
        # ******************************
        demand_lots = 0
        ave_demand_lots = 0
        ave_demand_lots_int = 0

        for w in range(53 * node.plan_range):
            demand_lots += len(node.psi4demand[w][0])

        ave_demand_lots = demand_lots / (53 * node.plan_range)

        # float2int
        ave_demand_lots_int = float2int(ave_demand_lots)


        # **** networkX demand *********
        # set demand on leaf_node    
        # weekly average demand by lot
        # ******************************
        node.nx_demand = ave_demand_lots_int


        total_demand += ave_demand_lots_int

    else:

        for child in node.children:

            # "行き" GOing on the way

            total_demand = set_leaf_demand(child, total_demand)


            # "帰り" RETURNing on the way BACK
            node.nx_demand = child.nx_demand  # set "middle_node" demand


    return total_demand







def show_network_E2E_matplotlib_OLD(
        root_node_outbound,    # instance pointor
        nodes_outbound,        # dictionary for nodes[name]=instance 
        root_node_inbound,
        nodes_inbound,    
        G, Gdm, Gsp ):

    root_node_name_out = root_node_outbound.name # name
    root_node_name_in  = root_node_inbound.name


    #@STOP 以下の二つに分解して定義
    ## *********************
    ## demand side
    ## treeのleaf nodesを探索してG.add_nodeを処理すると同時にtotal_demandを集計
    ## *********************
    #total_demand = 0
    #total_demand = G_add_nodes_tree(root_node_outbound, G, total_demand)


    # *********************
    # demand side
    # 1. treeのleaf nodesを探索してweekly average demandをleafにセット
    # 2. weekly average demandのtotalをroot=mother plantにセット
    # *********************
    # weekly average demand by lot

    total_demand =0
    total_demand =set_leaf_demand(root_node_outbound, total_demand)

    print("average_total_demand", total_demand)
    print("root_node_outbound.nx_demand", root_node_outbound.nx_demand)


    # **** networkX demand *********
    # set root demand ( mother plant and all suppliers )
    # ******************************

    # **** all suppliers can get this total_demand via root_node_name_"in=out"
    root_node_outbound.nx_demand = total_demand  
    root_node_inbound.nx_demand = total_demand  

    # *********************
    # G.add_node()  from both demand & supply side
    # IN and OUT treeのleaf nodesを探索してG.add_nodeを処理する 
    # node_nameをGにセット (X,Y)はfreeな状態、(X,Y)のsettingは後処理
    # *********************

    G_add_nodes_from_tree(root_node_outbound, G)

    G_add_nodes_from_tree_skip_root(root_node_inbound, root_node_name_in, G)


    # *****************
    # adding "sales_office" node on G G.add_node("sales_office"
    # *****************
    # "sales_office"は最終需要の集計管理用 demand属性を総需要に更新
    # G.nodes["sales_office"]["demand"] = total_demand

    #@240901 "sales_office" is dupplicated
    G.add_node("sales_office", demand=total_demand)  # total_demandはINT

    G.add_node(root_node_outbound.name, demand=0 )   # root / mother_plantを0に

    G.add_node("procurement_office", demand=(-1 * total_demand) )

    print("G.add_node sales_office total_demand=", total_demand)
    print("G.add_node procurement_office total_demand=", (-1 * total_demand))



    # *****************
    # 親子関係をadd_edge
    # *****************

    # outbound
    G_add_edge_from_tree(root_node_outbound, G)

    # capacity = weekly_average * N倍
    supplyers_capacity = root_node_inbound.nx_demand * 2 # weekly_average

    # inbound
    G_add_edge_from_inbound_tree(root_node_inbound, supplyers_capacity, G)




    # outbound for optimise
    G_add_nodes_from_tree(root_node_outbound, Gdm)
    Gdm.add_node(root_node_outbound.name, demand = (-1 * total_demand))
    Gdm.add_node("sales_office", demand = total_demand )

    Gdm_add_edge_sc2nx_outbound(root_node_outbound, Gdm)



    # inbound for optimise
    G_add_nodes_from_tree(root_node_inbound, Gsp)
    Gsp.add_node("procurement_office", demand = (-1 * total_demand) )
    Gsp.add_node(root_node_inbound.name, demand = total_demand)

    Gsp_add_edge_sc2nx_inbound(root_node_inbound, Gsp)




    #@241205 STOP Init_loading is just display. Optimise is follow
    ## *********************
    ## 最小費用流問題を解く
    ## *********************
    ## NetworkXの`network_simplex`関数を使用して、最小費用流問題を解く。
    #
    ## ネットワークのノードとエッジの属性を出力
    #print("ノードの需要とエッジのキャパシティを確認")
    ##for node in Gdm.nodes(data=True):
    ##    print("Gdm",node)
    ##for edge in Gdm.edges(data=True):
    ##    print("Gdm",edge)
    #
    ## *********************
    ## 最適化solver for demand side Gdm
    ## *********************
    #flowCost_dm, flowDict_dm = nx.network_simplex(Gdm)
    #
    #
    ## ネットワークのノードとエッジの属性を出力
    #print("ノードの需要とエッジのキャパシティを確認")
    ##for node in Gsp.nodes(data=True):
    ##    print("Gsp",node)
    ##for edge in Gsp.edges(data=True):
    ##    print("Gsp",edge)
    #
    ## *********************
    ## 最適化solver for demand side Gsp
    ## *********************
    #
    #flowCost_sp, flowDict_sp = nx.network_simplex(Gsp)


    #@240902 STOP
    ## *********************
    ## 最小カットの計算
    ## *********************
    #cut_value, partition = nx.minimum_cut( 
    #    Gsp,
    #    "procurement_office", root_node_inbound.name,
    #    capacity='capacity'
    #)
    #
    #reachable, non_reachable = partition
    #
    #print(f"Cut value: {cut_value}")
    #print(f"Reachable nodes: {reachable}")
    #print(f"Non-reachable nodes: {non_reachable}")




    # *********************
    # 需要と供給のバランスを取る
    # *********************

    # 対処方法
    # 1. **ノードの需要と供給を確認する**:
    for node in G.nodes(data=True):
       #print("需要と供給を確認")
        print(node)

    # 2. 需要と供給のバランスを取る
    #   需要と供給のバランスが取れていない場合、適切に調整
    #   例えば、供給ノードの需要を減らすか、需要ノードの供給を増やすなど

    # 3. ダミーノードを追加する
    #   需要と供給のバランスを取るために、ダミーノードを追加する
    #   ダミーノードは、余分な需要や供給を吸収するために使用される

    # **********************
    # ダミーノードを追加してバランスを取る例
    # **********************
    ## 需要と供給の合計を計算
    #total_demand = sum(data['demand'] for node, data in G.nodes(data=True))
    #
    ## ダミーノードを追加
    #if total_demand != 0:
    #    G.add_node('dummy', demand=-total_demand)
    #    for node in G.nodes():
    #        if node != 'dummy':
    #            G.add_edge(node, 'dummy', weight=0)



    # ネットワークのノードとエッジの属性を出力
    print("ノードの需要とエッジのキャパシティを確認")

    for node in G.nodes(data=True):
        print(node)

    for edge in G.edges(data=True):
        print(edge)


    # debug用 需給の確認
    print("demandの確認",)

    for node, data in G.nodes(data=True):
        print(f"Node: {node}, Demand: {data.get('demand', 0)}")




    # *********************
    # 最適化solver
    # *********************

    #@240901 STOP optimising proc for going visualising
    #flowCost, flowDict = nx.network_simplex(G)


    #@240831 TO BE DEFINE
    # *********************
    # treeからposを生成
    # *********************

    # End 2 End network nodes position
    pos_E2E = make_E2E_positions(root_node_outbound, root_node_inbound)

    pos_E2E = tune_hammock(pos_E2E, nodes_outbound, nodes_inbound)



    # ****************************
    # graph with matplotlib
    # ****************************

    ## グラフ描画関数を呼び出し
    #draw_network(G, Gdm, Gsp, pos_E2E, flowDict_dm, flowDict_sp)

    return pos_E2E, Gdm, Gsp
    #return pos_E2E, flowDict_dm, flowDict_sp, Gdm, Gsp








def sum_all_revenue_profit(node, total_revenue, total_profit):

    total_revenue += node.eval_revenue
    total_profit  += node.eval_profit

    if node.children == []: # leaf_node

        pass

    for child in node.children:

        sum_all_revenue_profit(child, total_revenue, total_profit)

    return total_revenue, total_profit



def eval_plan_kpi(root_node_outbound, root_node_inbound):
#def eval_plan(nodes):

    t_rev    = 0
    t_prof   = 0

    t_rev, t_prof = sum_all_revenue_profit(root_node_outbound, t_rev, t_prof)
    t_rev, t_prof = sum_all_revenue_profit(root_node_inbound, t_rev, t_prof)


    node_summaries = []


#    for node in nodes:
#        revenue = sum(data.get('revenue', 0) for data in node.data)
#        profit = sum(data.get('profit', 0) for data in node.data)
#        node_summaries.append({
#            "node_name": node.name,
#            "revenue": revenue,
#            "profit": profit
#        })
#        total_revenue += revenue
#        total_profit += profit


    ##@241105 test
    #t_rev   = 123000000
    #t_prof  = 23400000

    node_summaries = ["here is ","node by node","revenue:333","profit:111"]


    return {
        "total_revenue": t_rev,
        "total_profit": t_prof,
        "node_summaries": node_summaries
    }


# ******************************
# recursive call for Planning ENGINE
# ******************************




# ******************************
# in or out    : root_node_outbound
# plan layer   : demand layer
# node order   : preorder # Leaf2Root
# time         : Foreward
# calculation  : PS2I
# ******************************
def calc_all_psi2i4demand(node):

    node.calcPS2I4demand()

    for child in node.children:

        calc_all_psi2i4demand(child)






# ******************************
# Evaluation process
# ******************************

def set_price_leaf2root(node, root_node_outbound, val):

    #print("node.name ", node.name)
    root_price = 0

    pb = 0
    pb = node.price_sales_shipped  # pb : Price_Base

    # set value on shipping price
    node.cs_price_sales_shipped = val

    print("def set_price_leaf2root", node.name, node.cs_price_sales_shipped )

    node.show_sum_cs()



    # cs : Cost_Stracrure
    node.cs_cost_total = val * node.cost_total / pb
    node.cs_profit = val * node.profit / pb
    node.cs_marketing_promotion = val * node.marketing_promotion / pb
    node.cs_sales_admin_cost = val * node.sales_admin_cost / pb
    node.cs_SGA_total = val * node.SGA_total / pb
    node.cs_custom_tax = val * node.custom_tax / pb
    node.cs_tax_portion = val * node.tax_portion / pb
    node.cs_logistics_costs = val * node.logistics_costs / pb
    node.cs_warehouse_cost = val * node.warehouse_cost / pb

    # direct shipping price that is,  like a FOB at port
    node.cs_direct_materials_costs = val * node.direct_materials_costs / pb

    node.cs_purchase_total_cost = val * node.purchase_total_cost / pb
    node.cs_prod_indirect_labor = val * node.prod_indirect_labor / pb
    node.cs_prod_indirect_others = val * node.prod_indirect_others / pb
    node.cs_direct_labor_costs = val * node.direct_labor_costs / pb
    node.cs_depreciation_others = val * node.depreciation_others / pb
    node.cs_manufacturing_overhead = val * node.manufacturing_overhead / pb

    #print("probe")
    #node.show_sum_cs()

    #print("node.cs_direct_materials_costs", node.name, node.cs_direct_materials_costs)
    #print("root_node_outbound.name", root_node_outbound.name)


    if node.name == root_node_outbound.name:
    #if node == root_node_outbound:

        node.cs_profit_accume = node.cs_profit # profit_accumeの初期セット

        root_price = node.cs_price_sales_shipped
        # root_price = node.cs_direct_materials_costs

        pass

    else:

        root_price = set_price_leaf2root(
            node.parent, root_node_outbound, node.cs_direct_materials_costs
        )

    return root_price




# 1st val is "root_price"
# 元の売値=valが、先の仕入れ値=pb Price_Base portionになる。
def set_value_chain_outbound(val, node):


    # root_nodeをpassして、子供からstart


    # はじめは、root_nodeなのでnode.childrenは存在する
    for child in node.children:

        #print("set_value_chain_outbound child.name ", child.name)
        # root_price = 0

        pb = 0
        pb = child.direct_materials_costs  # pb : Price_Base portion

        print("child.name", child.name)
        print("pb = child.direct_materials_costs",child.direct_materials_costs)

        # pb = child.price_sales_shipped # pb : Price_Base portion

        # direct shipping price that is,  like a FOB at port

        child.cs_direct_materials_costs = val

        # set value on shipping price
        child.cs_price_sales_shipped = val * child.price_sales_shipped / pb
        #print("def set_value_chain_outbound", child.name, child.cs_price_sales_shipped )
        child.show_sum_cs()



        val_child = child.cs_price_sales_shipped

        # cs : Cost_Stracrure
        child.cs_cost_total = val * child.cost_total / pb

        child.cs_profit = val * child.profit / pb

        # root2leafまでprofit_accume
        child.cs_profit_accume += node.cs_profit

        child.cs_marketing_promotion = val * child.marketing_promotion / pb
        child.cs_sales_admin_cost = val * child.sales_admin_cost / pb
        child.cs_SGA_total = val * child.SGA_total / pb
        child.cs_custom_tax = val * child.custom_tax / pb
        child.cs_tax_portion = val * child.tax_portion / pb
        child.cs_logistics_costs = val * child.logistics_costs / pb
        child.cs_warehouse_cost = val * child.warehouse_cost / pb

        ## direct shipping price that is,  like a FOB at port
        # node.cs_direct_materials_costs = val * node.direct_materials_costs / pb

        child.cs_purchase_total_cost = val * child.purchase_total_cost / pb
        child.cs_prod_indirect_labor = val * child.prod_indirect_labor / pb
        child.cs_prod_indirect_others = val * child.prod_indirect_others / pb
        child.cs_direct_labor_costs = val * child.direct_labor_costs / pb
        child.cs_depreciation_others = val * child.depreciation_others / pb
        child.cs_manufacturing_overhead = val * child.manufacturing_overhead / pb

        #print("probe")
        #child.show_sum_cs()


        print(
            "node.cs_direct_materials_costs",
            child.name,
            child.cs_direct_materials_costs,
        )
        # print("root_node_outbound.name", root_node_outbound.name )

        # to be rewritten@240803

        if child.children == []:  # leaf_nodeなら終了

            pass

        else:  # 孫を処理する

            set_value_chain_outbound(val_child, child)

    # return







# ******************************
# Graph process
# ******************************
#def show_psi(child, DS_flag, week_start, week_end):
#def show_psi(node):


#import pandas as pd
#import matplotlib.pyplot as plt

#import pandas as pd
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import tkinter as tk
#from tkinter import ttk












def map_psi_lots2df(node, D_S_flag, psi_lots):
    if D_S_flag == "demand":
        matrix = node.psi4demand
    elif D_S_flag == "supply":
        matrix = node.psi4supply
    else:
        print("error: wrong D_S_flag is defined")
        return pd.DataFrame()

    for week, row in enumerate(matrix):
        for scoip, lots in enumerate(row):
            for step_no, lot_id in enumerate(lots):
                psi_lots.append([node.name, week, scoip, step_no, lot_id])

    for child in node.children:
        map_psi_lots2df(child, D_S_flag, psi_lots)

    columns = ["node_name", "week", "s-co-i-p", "step_no", "lot_id"]
    df = pd.DataFrame(psi_lots, columns=columns)
    return df


# **************************
# collect_psi_data
# **************************
def collect_psi_data(node, D_S_flag, week_start, week_end, psi_data):
    if D_S_flag == "demand":
        psi_lots = []
        df_demand_plan = map_psi_lots2df(node, D_S_flag, psi_lots)
        df_init = df_demand_plan
    elif D_S_flag == "supply":
        psi_lots = []
        df_supply_plan = map_psi_lots2df(node, D_S_flag, psi_lots)
        df_init = df_supply_plan
    else:
        print("error: D_S_flag should be demand or supply")
        return

    condition1 = df_init["node_name"] == node.name
    condition2 = (df_init["week"] >= week_start) & (df_init["week"] <= week_end)
    df = df_init[condition1 & condition2]

    line_data_2I = df[df["s-co-i-p"].isin([2])]
    bar_data_0S = df[df["s-co-i-p"] == 0]
    bar_data_3P = df[df["s-co-i-p"] == 3]

    line_plot_data_2I = line_data_2I.groupby("week")["lot_id"].count()
    bar_plot_data_3P = bar_data_3P.groupby("week")["lot_id"].count()
    bar_plot_data_0S = bar_data_0S.groupby("week")["lot_id"].count()



    # ノードのREVENUEとPROFITを四捨五入

    # root_out_optからroot_outboundの世界へ変換する
    #@241225 be checked

    #@ STOP
    ##@ TEST node_optとnode_originに、revenueとprofit属性を追加
    #revenue = round(node.revenue)
    #profit  = round(node.profit)


    #@241225 STOP "self.nodes_outbound"がscopeにない
    #node_origin = self.nodes_outbound[node.name]
    #

    revenue = round(node.eval_cs_price_sales_shipped)
    profit = round(node.eval_cs_profit)



    # PROFIT_RATIOを計算して四捨五入
    profit_ratio = round((profit / revenue) * 100, 1) if revenue != 0 else 0

    psi_data.append((node.name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S))



# node is "node_opt"
def collect_psi_data_opt(node, node_out, D_S_flag, week_start, week_end, psi_data):
    if D_S_flag == "demand":
        psi_lots = []
        df_demand_plan = map_psi_lots2df(node, D_S_flag, psi_lots)
        df_init = df_demand_plan
    elif D_S_flag == "supply":
        psi_lots = []
        df_supply_plan = map_psi_lots2df(node, D_S_flag, psi_lots)
        df_init = df_supply_plan
    else:
        print("error: D_S_flag should be demand or supply")
        return

    condition1 = df_init["node_name"] == node.name
    condition2 = (df_init["week"] >= week_start) & (df_init["week"] <= week_end)
    df = df_init[condition1 & condition2]

    line_data_2I = df[df["s-co-i-p"].isin([2])]
    bar_data_0S = df[df["s-co-i-p"] == 0]
    bar_data_3P = df[df["s-co-i-p"] == 3]

    line_plot_data_2I = line_data_2I.groupby("week")["lot_id"].count()
    bar_plot_data_3P = bar_data_3P.groupby("week")["lot_id"].count()
    bar_plot_data_0S = bar_data_0S.groupby("week")["lot_id"].count()



    # ノードのREVENUEとPROFITを四捨五入

    # root_out_optからroot_outboundの世界へ変換する
    #@241225 be checked

    #@ STOP
    ##@ TEST node_optとnode_originに、revenueとprofit属性を追加
    #revenue = round(node.revenue)
    #profit  = round(node.profit)


    #@241225 STOP "self.nodes_outbound"がscopeにない
    #node_origin = self.nodes_outbound[node.name]
    #

    # nodeをoptからoutに切り替え
    revenue = round(node_out.eval_cs_price_sales_shipped)
    profit = round(node_out.eval_cs_profit)



    # PROFIT_RATIOを計算して四捨五入
    profit_ratio = round((profit / revenue) * 100, 1) if revenue != 0 else 0

    psi_data.append((node.name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S))







# **************************
# show_all_psi
# **************************
def show_all_psi(root_node, D_S_flag, week_start, week_end):
    psi_data = []

    def traverse_nodes(node):
        for child in node.children:
            traverse_nodes(child)
        collect_psi_data(node, D_S_flag, week_start, week_end, psi_data)

    traverse_nodes(root_node)

    # Tkinterのセットアップ
    root = tk.Tk()
    root.title("Network Graph & PSI Graphs")

    # 全体のフレーム
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # 左側のNetwork Graphフレーム
    network_frame = ttk.Frame(main_frame)
    network_frame.pack(side="left", fill="both", expand=True)

    # 右側のPSI Graphスクロール可能フレーム
    psi_frame = ttk.Frame(main_frame)
    psi_frame.pack(side="right", fill="both", expand=True)


    # Network Graphを作成

    G = nx.DiGraph()

    for node in root_node.get_all_nodes():
        G.add_node(node.name)
        for child in node.children:
            G.add_edge(node.name, child.name)

    fig_network, ax_network = plt.subplots(figsize=(10, 5))

    pos = nx.spring_layout(G)

    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", ax=ax_network)

    canvas_network = FigureCanvasTkAgg(fig_network, master=network_frame)
    canvas_network.draw()
    canvas_network.get_tk_widget().pack()

    # PSI Graphを作成
    canvas = tk.Canvas(psi_frame)
    scrollbar = ttk.Scrollbar(psi_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    fig_psi, axs = plt.subplots(len(psi_data), 1, figsize=(10, len(psi_data) * 1))  # figsizeの高さをさらに短く設定

    if len(psi_data) == 1:
        axs = [axs]



    for ax, (node_name, revenue, profit, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S) in zip(axs, psi_data):
        ax2 = ax.twinx()

        ax.bar(line_plot_data_2I.index, line_plot_data_2I.values, color='r', alpha=0.6)
        ax.bar(bar_plot_data_3P.index, bar_plot_data_3P.values, color='g', alpha=0.6)
        ax2.plot(bar_plot_data_0S.index, bar_plot_data_0S.values, color='b')

        ax.set_xlim(week_start, week_end)  # 横軸の表示範囲を固定
        ax.set_ylabel('I&P Lots', fontsize=8)
        ax2.set_ylabel('S Lots', fontsize=8)
        ax.set_title(f'Node: {node_name}\nREVENUE: {revenue:,}\nPROFIT: {profit:,}', fontsize=8)



    fig_psi.tight_layout(pad=0.5)  # サブプロットの間隔をさらに小さく調整
    canvas_psi = FigureCanvasTkAgg(fig_psi, master=scrollable_frame)
    canvas_psi.draw()
    canvas_psi.get_tk_widget().pack()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()





# **************************
# cost_stracture
# **************************

def make_stack_bar4cost_stracture(cost_dict):
    attributes_B = [
        'cs_direct_materials_costs',
        'cs_marketing_promotion',
        'cs_sales_admin_cost',
        'cs_tax_portion',
        'cs_logistics_costs',
        'cs_warehouse_cost',
        'cs_prod_indirect_labor',
        'cs_prod_indirect_others',
        'cs_direct_labor_costs',
        'cs_depreciation_others',
        'cs_profit',
    ]

    colors = {
        'cs_direct_materials_costs': 'lightgray',
        'cs_marketing_promotion': 'darkblue',
        'cs_sales_admin_cost': 'blue',
        'cs_tax_portion': 'gray',
        'cs_logistics_costs': 'cyan',
        'cs_warehouse_cost': 'magenta',
        'cs_prod_indirect_labor': 'green',
        'cs_prod_indirect_others': 'lightgreen',
        'cs_direct_labor_costs': 'limegreen',
        'cs_depreciation_others': 'yellowgreen',
        'cs_profit': 'gold',
    }

    nodes = list(cost_dict.keys())
    bar_width = 0.5

    # Initialize the bottom of the bars
    bottoms = np.zeros(len(nodes))

    fig, ax = plt.subplots()

    for attr in attributes_B:
        values = [cost_dict[node][attr] for node in cost_dict]
        ax.bar(nodes, values, bar_width, label=attr, color=colors[attr], bottom=bottoms)
        bottoms += values

        # Add text on bars
        for i, value in enumerate(values):
            if value > 0:
                ax.text(i, bottoms[i] - value / 2, f'{value:.1f}', ha='center', va='center', fontsize=8, color='white')

    # Add total values on top of bars
    total_values = [sum(cost_dict[node][attr] for attr in attributes_B) for node in cost_dict]
    for i, total in enumerate(total_values):
        ax.text(i, total + 2, f'{total:.1f}', ha='center', va='bottom', fontsize=10)

    ax.set_title('Supply Chain Cost Structure on Common Planning Unit')
    ax.set_xlabel('Node')
    ax.set_ylabel('Amount')
    ax.legend(title='Attribute')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()




def show_nodes_cs_lot_G_Sales_Procure(root_node_outbound, root_node_inbound):


    # 属性名のリスト
    attributes = [
            'cs_direct_materials_costs',
            'cs_marketing_promotion',
            'cs_sales_admin_cost',
            'cs_tax_portion',
            'cs_logistics_costs',
            'cs_warehouse_cost',
            'cs_prod_indirect_labor',
            'cs_prod_indirect_others',
            'cs_direct_labor_costs',
            'cs_depreciation_others',
            'cs_profit',
        ]



    #属性毎の辞書をリストにして、node辞書にする
    # postordering
    def dump_node_amt_all_in(node, node_amt_all):

        for child in node.children:
            dump_node_amt_all_in(child, node_amt_all)


        # 属性値のリストを作成 
        #amt_list = {attr: sum( getattr(node, attr) )  for attr in attributes}

        amt_list = {attr: getattr(node, attr) for attr in attributes}

        if node.name == "JPN":

            node_amt_all["JPN_IN"] = amt_list

        else:

            node_amt_all[node.name] = amt_list

        return node_amt_all



    #属性毎の辞書をリストにして、node辞書にする
    # preordering
    def dump_node_amt_all_out(node, node_amt_all):

        # 属性値のリストを作成 
        #amt_list = {attr: sum( getattr(node, attr) )  for attr in attributes}

        amt_list = {attr: getattr(node, attr) for attr in attributes}

        #@240918 STOP
        #node_amt_all[node.name] = amt_list

        if node.name == "JPN":

            node_amt_all["JPN_OUT"] = amt_list

            #print("JPN_OUT amt_list",amt_list)

        else:

            node_amt_all[node.name] = amt_list


        for child in node.children:
            dump_node_amt_all_out(child, node_amt_all)

        return node_amt_all



    node_amt_sum_in = {}
    node_amt_sum_in = dump_node_amt_all_in(root_node_inbound, {} )  #postorder

    node_amt_sum_out = {}
    node_amt_sum_out = dump_node_amt_all_out(root_node_outbound, {} ) #preorder

    # node_amt_sum_inとnode_amt_sum_outをマージしてnode_amt_sum_in_outを作成
    node_amt_sum_in_out = {**node_amt_sum_in, **node_amt_sum_out}


    #node_amt_sum = dump_node_amt_all(root_node_inbound, node_amt_sum)

    #print("node_amt_sum_in",node_amt_sum_in)

    #@241118 RUN
    print("node_amt_sum_out",node_amt_sum_out)


    #@STOP
    #make_stack_bar4cost_stracture(node_amt_sum_in_out)
    #make_stack_bar4cost_stracture(node_amt_sum_in)

    make_stack_bar4cost_stracture(node_amt_sum_out)


# ****************************
# tree positioing test
# ****************************
def set_positions_recursive(node, width_tracker):
    for child in node.children:
        child.depth = node.depth + 1
        child.width = width_tracker[child.depth]
        width_tracker[child.depth] += 1
        set_positions_recursive(child, width_tracker)

def adjust_positions(node):
    if not node.children:
        return node.width

    children_y_min = min(adjust_positions(child) for child in node.children)
    children_y_max = max(adjust_positions(child) for child in node.children)
    node.width = (children_y_min + children_y_max) / 2

    for i, child in enumerate(node.children):
        child.width += i * 0.1

    return node.width

def set_positions(root):
    width_tracker = [0] * 100
    set_positions_recursive(root, width_tracker)
    adjust_positions(root)

def show_tree(root):
    set_positions(root)
    G = nx.DiGraph()
    nodes = {}

    def add_edges(node):
        nodes[node.name] = node
        for child in node.children:
            G.add_edge(node.name, child.name)
            add_edges(child)

    add_edges(root)

    pos = {name: (node.width, -node.depth) for name, node in nodes.items()}
    labels = {name: name for name in nodes}

    plt.figure()  # 新しいフィギュアを作成

    nx.draw(G, pos, labels=labels, with_labels=True, arrows=False, node_size=100, node_color="skyblue")

    plt.show()
        




def is_picklable(value):
    try:
        pickle.dumps(value)
    except (pickle.PicklingError, TypeError):
        return False
    return True







class PSIPlannerApp4save:

    #def __init__(self, root):

    def __init__(self):

        #self.root = root
        #self.root.title("Global Weekly PSI Planner")

        self.root_node = None  # root_nodeの定義を追加


        self.lot_size     = 2000      # 初期値

        self.plan_year_st = 2022      # 初期値
        self.plan_range   = 2         # 初期値

        self.pre_proc_LT  = 13        # 初期値 13week = 3month


        self.market_potential = 0     # 初期値 0
        self.target_share     = 0.5   # 初期値 0.5 = 50%
        self.total_supply     = 0     # 初期値 0


        #@ STOP
        #self.setup_ui()

        self.outbound_data = None
        self.inbound_data = None

        # PySI tree
        self.root_node_outbound = None
        self.nodes_outbound     = None
        self.leaf_nodes_out     = []

        self.root_node_inbound  = None
        self.nodes_inbound      = None
        self.leaf_nodes_in      = []

        self.root_node_out_opt  = None
        self.nodes_out_opt      = None
        self.leaf_nodes_opt     = []


        self.optimized_root     = None
        self.optimized_nodes    = None


        # Evaluation on PSI
        self.total_revenue = 0
        self.total_profit  = 0
        self.profit_ratio  = 0


        # view
        self.G = None

        # Optimise
        self.Gdm_structure = None

        self.Gdm = None
        self.Gsp = None

        self.pos_E2E = None

        self.flowDict_opt = {} #None
        self.flowCost_opt = {} #None

        self.total_supply_plan = 0

        # loading files
        self.directory = None
        self.load_directory = None

        self.base_leaf_name = None

        # supply_plan / decoupling / buffer stock
        self.decouple_node_dic = {}

        self.decouple_node_selected = []



    #@ STOP
    #def update_from_psiplannerapp(self, psi_planner_app):
    #    self.__dict__.update(psi_planner_app.__dict__)
    #
    #def update_psiplannerapp(self, psi_planner_app):
    #    psi_planner_app.__dict__.update(self.__dict__)



#@ STOP
#    def update_from_psiplannerapp(self, psi_planner_app):
#        attributes = {key: value for key, value in psi_planner_app.__dict__.items() if key != 'root'}
#        self.__dict__.update(attributes)
#
#    def update_psiplannerapp(self, psi_planner_app):
#        attributes = {key: value for key, value in self.__dict__.items()}
#        psi_planner_app.__dict__.update(attributes)



    def update_from_psiplannerapp(self, psi_planner_app):
        attributes = {key: value for key, value in psi_planner_app.__dict__.items()
                      if key != 'root' and is_picklable(value) and not isinstance(value, (tk.Tk, tk.Widget, tk.Toplevel, tk.Variable))}
        self.__dict__.update(attributes)

    def update_psiplannerapp(self, psi_planner_app):
        attributes = {key: value for key, value in self.__dict__.items()}
        psi_planner_app.__dict__.update(attributes)







    #@ STOP
    #def update_psiplannerapp(self, psi_planner_app):
    #    psi_planner_app.root_node = self.root_node
    #    psi_planner_app.D_S_flag = self.D_S_flag
    #    psi_planner_app.week_start = self.week_start
    #    psi_planner_app.week_end = self.week_end
    #    psi_planner_app.decouple_node_selected = self.decouple_node_selected
    #    psi_planner_app.G = self.G
    #    psi_planner_app.Gdm = self.Gdm
    #    psi_planner_app.Gdm_structure = self.Gdm_structure
    #    psi_planner_app.Gsp = self.Gsp
    #    psi_planner_app.pos_E2E = self.pos_E2E







class PSIPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Weekly PSI Planner")



        self.lot_size     = 2000      # 初期値

        self.plan_year_st = 2022      # 初期値
        self.plan_range   = 2         # 初期値

        self.pre_proc_LT  = 13        # 初期値 13week = 3month


        self.market_potential = 0     # 初期値 0
        self.target_share     = 0.5   # 初期値 0.5 = 50%
        self.total_supply     = 0     # 初期値 0



        self.setup_ui()

        self.outbound_data = None
        self.inbound_data = None

        # PySI tree
        self.root_node_outbound = None
        self.nodes_outbound     = None
        self.leaf_nodes_out     = []

        self.root_node_inbound  = None
        self.nodes_inbound      = None
        self.leaf_nodes_in      = []

        self.root_node_out_opt  = None
        self.nodes_out_opt      = None
        self.leaf_nodes_opt     = []


        self.optimized_root     = None
        self.optimized_nodes    = None


        # Evaluation on PSI
        self.total_revenue = 0
        self.total_profit  = 0
        self.profit_ratio  = 0


        # view
        self.G = None

        # Optimise
        self.Gdm_structure = None

        self.Gdm = None
        self.Gsp = None

        self.pos_E2E = None

        self.flowDict_opt = {} #None
        self.flowCost_opt = {} #None

        self.total_supply_plan = 0

        # loading files
        self.directory = None
        self.load_directory = None

        self.base_leaf_name = None

        # supply_plan / decoupling / buffer stock
        self.decouple_node_dic = {}

        self.decouple_node_selected = []




    
    #@STOP
    #def load_data(self, filename="saved_data.pkl"):
    #    with open(filename, "rb") as f:
    #        loaded_attributes = pickle.load(f)
    #    psi_planner_app_save = PSIPlannerApp4save()
    #    psi_planner_app_save.__dict__.update(loaded_attributes)
    #    psi_planner_app_save.update_psiplannerapp(self)
    #    print("データをロードしました。")


    #@ STOP this is a sample code for "by PSIPlannerApp4save class definition"
    #def load_data(self, load_directory):
    #    with open(os.path.join(load_directory, 'psi_planner_app.pkl'), "rb") as f:
    #        loaded_attributes = pickle.load(f)
    #
    #    psi_planner_app_save = PSIPlannerApp4save()
    #    psi_planner_app_save.__dict__.update(loaded_attributes)
    #
    #    psi_planner_app_save.update_psiplannerapp(self)
    #    print("データをロードしました。")









    def load_data(self, load_directory):
        with open(os.path.join(load_directory, 'psi_planner_app.pkl'), "rb") as f:
            loaded_attributes = pickle.load(f)

    #@ STOP this is a sample code for "fixed file"
    #def load_data(self, filename="saved_data.pkl"):
    #    with open(filename, "rb") as f:
    #        loaded_attributes = pickle.load(f)


        psi_planner_app_save = PSIPlannerApp4save()
        psi_planner_app_save.__dict__.update(loaded_attributes)
        
        # 選択的にインスタンス変数を更新
        self.root_node = psi_planner_app_save.root_node


        #@ STOP
        #self.D_S_flag = psi_planner_app_save.D_S_flag
        #self.week_start = psi_planner_app_save.week_start
        #self.week_end = psi_planner_app_save.week_end

        self.decouple_node_selected=psi_planner_app_save.decouple_node_selected


        self.G = psi_planner_app_save.G
        self.Gdm = psi_planner_app_save.Gdm
        self.Gdm_structure = psi_planner_app_save.Gdm_structure
        self.Gsp = psi_planner_app_save.Gsp
        self.pos_E2E = psi_planner_app_save.pos_E2E

        self.total_revenue = psi_planner_app_save.total_revenue
        print("load_data: self.total_revenue", self.total_revenue)
        self.total_profit = psi_planner_app_save.total_profit
        print("load_data: self.total_profit", self.total_profit)

        self.flowDict_opt = psi_planner_app_save.flowDict_opt
        self.flowCost_opt = psi_planner_app_save.flowCost_opt


        self.market_potential = psi_planner_app_save.market_potential
        print("self.market_potential", self.market_potential)

        self.target_share = psi_planner_app_save.target_share
        print("self.target_share", self.target_share)

        # エントリウィジェットに反映する
        self.ts_entry.delete(0, tk.END)
        self.ts_entry.insert(0, f"{self.target_share * 100:.0f}")  # 保存された値を反映



        print(f"読み込み時 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加
        print("データをロードしました。")
    
    
    
    



    def setup_ui(self):

        print("setup_ui is processing")

        # フォントの設定
        custom_font = tkfont.Font(family="Helvetica", size=12)

        # メニュー全体のフォントサイズを設定
        self.root.option_add('*TearOffMenu*Font', custom_font)
        self.root.option_add('*Menu*Font', custom_font)

        # メニューバーの作成
        menubar = tk.Menu(self.root)

        # スタイルの設定
        style = ttk.Style()
        style.configure("TMenubutton", font=("Helvetica", 12))

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="OPEN: select Directory", command=self.load_data_files)
        file_menu.add_separator()
        file_menu.add_command(label="SAVE: to Directory", command=self.save_to_directory)

        file_menu.add_command(label="LOAD: from Directory", command=self.load_from_directory)

        file_menu.add_separator()
        file_menu.add_command(label="EXIT", command=self.on_exit)
        menubar.add_cascade(label=" FILE  ", menu=file_menu)

        # Optimize Parameter menu
        optimize_menu = tk.Menu(menubar, tearoff=0)
        optimize_menu.add_command(label="Weight: Cost Stracture on Common Plan Unit", command=self.show_cost_stracture_bar_graph)
        optimize_menu.add_command(label="Capacity: Market Demand", command=self.show_month_data_csv)
        menubar.add_cascade(label="Optimize Parameter", menu=optimize_menu)



        # Report menu
        report_menu = tk.Menu(menubar, tearoff=0)

        report_menu.add_command(label="Outbound: PSI to csv file", command=self.outbound_psi_to_csv)

        report_menu.add_command(label="Outbound: Lot by Lot data to csv", command=self.outbound_lot_by_lot_to_csv)

        report_menu.add_separator()

        report_menu.add_command(label="Inbound: PSI to csv file", command=self.inbound_psi_to_csv)
        report_menu.add_command(label="Inbound: Lot by Lot data to csv", command=self.inbound_lot_by_lot_to_csv)

        report_menu.add_separator()

        report_menu.add_separator()

        report_menu.add_command(label="Value Chain: Cost Stracture a Lot", command=self.lot_cost_structure_to_csv)

        report_menu.add_command(label="Supply Chain: Revenue Profit", command=self.supplychain_performance_to_csv)



        #report_menu.add_separator()
        #
        #report_menu.add_command(label="PSI for Excel", command=self.psi_for_excel)


        menubar.add_cascade(label="Report", menu=report_menu)




        # 3D overview menu
        overview_menu = tk.Menu(menubar, tearoff=0)
        overview_menu.add_command(label="3D overview on Lots based Plan", command=self.show_3d_overview)
        menubar.add_cascade(label="3D overview", menu=overview_menu)

        self.root.config(menu=menubar)

        # フレームの作成
        self.frame = ttk.Frame(self.root)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

        # Lot size entry
        self.lot_size_label = ttk.Label(self.frame, text="Lot Size:")
        self.lot_size_label.pack(side=tk.TOP)
        self.lot_size_entry = ttk.Entry(self.frame, width=10)
        self.lot_size_entry.pack(side=tk.TOP)
        self.lot_size_entry.insert(0, str(self.lot_size))  # 初期値を設定

        # Plan Year Start entry
        self.plan_year_label = ttk.Label(self.frame, text="Plan Year Start:")
        self.plan_year_label.pack(side=tk.TOP)
        self.plan_year_entry = ttk.Entry(self.frame, width=10)
        self.plan_year_entry.pack(side=tk.TOP)
        self.plan_year_entry.insert(0, str(self.plan_year_st))  # 初期値を設定

        # Plan Range entry
        self.plan_range_label = ttk.Label(self.frame, text="Plan Range:")
        self.plan_range_label.pack(side=tk.TOP)
        self.plan_range_entry = ttk.Entry(self.frame, width=10)
        self.plan_range_entry.pack(side=tk.TOP)
        self.plan_range_entry.insert(0, str(self.plan_range))  # 初期値を設定

        # 1行分の空白を追加
        self.space_label = ttk.Label(self.frame, text="")
        self.space_label.pack(side=tk.TOP)

        # Demand Planning buttons
        self.Demand_Pl_button = ttk.Button(self.frame, text="Demand Planning", command=self.demand_planning)
        self.Demand_Pl_button.pack(side=tk.TOP)

        # Plan Year Start entry
        self.pre_proc_LT_label = ttk.Label(self.frame, text="pre_proc_LT:")
        self.pre_proc_LT_label.pack(side=tk.TOP)
        self.pre_proc_LT_entry = ttk.Entry(self.frame, width=10)
        self.pre_proc_LT_entry.pack(side=tk.TOP)
        self.pre_proc_LT_entry.insert(0, str(self.pre_proc_LT))  # 初期値を設定

        # Demand Leveling button
        self.Demand_Lv_button = ttk.Button(self.frame, text="Demand Leveling", command=self.demand_leveling)
        self.Demand_Lv_button.pack(side=tk.TOP)

        # add a blank line
        self.space_label = ttk.Label(self.frame, text="")
        self.space_label.pack(side=tk.TOP)

        # Supply Planning button
        self.supply_planning_button = ttk.Button(self.frame, text="Supply Planning ", command=self.supply_planning)
        self.supply_planning_button.pack(side=tk.TOP)

        # add a blank line
        self.space_label = ttk.Label(self.frame, text="")
        self.space_label.pack(side=tk.TOP)

        # Eval_buffer_stock buttons
        self.eval_buffer_stock_button = ttk.Button(self.frame, text="Eval Buffer Stock ", command=self.eval_buffer_stock)
        self.eval_buffer_stock_button.pack(side=tk.TOP)

        # add a blank line
        self.space_label = ttk.Label(self.frame, text="")
        self.space_label.pack(side=tk.TOP)

        # Optimize Network button
        self.optimize_button = ttk.Button(self.frame, text="OPT Supply Alloc", command=self.optimize_network)
        self.optimize_button.pack(side=tk.TOP)

        # Plot area divided into two frames
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Network Graph frame
        self.network_frame = ttk.Frame(self.plot_frame)
        self.network_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # New Frame for Parameters at the top of the network_frame
        self.param_frame = ttk.Frame(self.network_frame)
        self.param_frame.pack(side=tk.TOP, fill=tk.X)


        # Global Market Potential, Target Share, Total Supply Plan input fields arranged horizontally
        self.gmp_label = tk.Label(self.param_frame, text="Market Potential:", background='navy', foreground='white', font=('Helvetica', 10, 'bold'))
        self.gmp_label.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=10)
        self.gmp_entry = tk.Entry(self.param_frame, width=10)
        self.gmp_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=10)

        self.ts_label = tk.Label(self.param_frame, text="TargetShare(%)", background='navy', foreground='white', font=('Helvetica', 10, 'bold'))
        self.ts_label.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=10)
        self.ts_entry = tk.Entry(self.param_frame, width=5)
        self.ts_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=10)
        self.ts_entry.insert(0, self.target_share * 100)

        self.tsp_label = tk.Label(self.param_frame, text="Total Supply:", background='navy', foreground='white', font=('Helvetica', 10, 'bold'))
        self.tsp_label.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=10)
        self.tsp_entry = tk.Entry(self.param_frame, width=10)
        self.tsp_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=10)
        self.tsp_entry.config(bg='lightgrey')  # 背景色をlightgreyに設定









        # イベントバインディング
        self.gmp_entry.bind("<Return>", self.update_total_supply_plan)
        self.ts_entry.bind("<Return>", self.update_total_supply_plan)

        self.fig_network, self.ax_network = plt.subplots(figsize=(4, 8))  # 横幅を縮小
        self.canvas_network = FigureCanvasTkAgg(self.fig_network, master=self.network_frame)
        self.canvas_network.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig_network.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        # Evaluation result area
        self.eval_frame = ttk.Frame(self.plot_frame)
        self.eval_frame.pack(side=tk.TOP, fill=tk.X, padx=(20, 0))  # 横方向に配置

        # Total Revenue
        self.total_revenue_label = ttk.Label(self.eval_frame, text="Total Revenue:", background='darkgreen', foreground='white', font=('Helvetica', 10, 'bold'))
        self.total_revenue_label.pack(side=tk.LEFT, padx=5, pady=10)
        self.total_revenue_entry = ttk.Entry(self.eval_frame, width=10, state='readonly')
        self.total_revenue_entry.pack(side=tk.LEFT, padx=5, pady=10)

        # Total Profit
        self.total_profit_label = ttk.Label(self.eval_frame, text="Total Profit:", background='darkgreen', foreground='white', font=('Helvetica', 10, 'bold'))
        self.total_profit_label.pack(side=tk.LEFT, padx=5, pady=10)
        self.total_profit_entry = ttk.Entry(self.eval_frame, width=10, state='readonly')
        self.total_profit_entry.pack(side=tk.LEFT, padx=5, pady=10)



        # Profit Ratio
        self.profit_ratio_label = ttk.Label(self.eval_frame, text="Profit Ratio:", background='darkgreen', foreground='white', font=('Helvetica', 10, 'bold'))
        self.profit_ratio_label.pack(side=tk.LEFT, padx=5, pady=10)
        self.profit_ratio_entry = ttk.Entry(self.eval_frame, width=10, state='readonly')
        self.profit_ratio_entry.pack(side=tk.LEFT, padx=5, pady=10)

        # PSI Graph scroll frame (moved to below evaluation area)
        self.psi_frame = ttk.Frame(self.plot_frame)
        self.psi_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas_psi = tk.Canvas(self.psi_frame)
        self.scrollbar = ttk.Scrollbar(self.psi_frame, orient="vertical", command=self.canvas_psi.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_psi)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_psi.configure(
                scrollregion=self.canvas_psi.bbox("all")
            )
        )

        self.canvas_psi.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas_psi.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_psi.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 初期化関数を呼び出してパラメータ設定
        self.initialize_parameters()


    def create_label_entry(self, parent, label_text, initial_value):
        label = ttk.Label(parent, text=label_text)
        label.pack(side=tk.TOP)
        entry = ttk.Entry(parent, width=10)
        entry.pack(side=tk.TOP)
        entry.insert(0, str(initial_value))  # 初期値を設定
        return entry

    def create_button(self, parent, button_text, command):
        button = ttk.Button(parent, text=button_text, command=command)
        button.pack(side=tk.TOP)

    def add_empty_line(self, parent):
        space_label = ttk.Label(parent, text="")
        space_label.pack(side=tk.TOP)



    def outbound_psi_to_csv(self):
        # ファイル保存ダイアログを表示して保存先ファイルパスを取得
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not save_path:
            return  # ユーザーがキャンセルした場合

        # 計画の出力期間を計算
        output_period_outbound = 53 * self.root_node_outbound.plan_range

        # データの収集
        data = []

        def collect_data(node, output_period):
            for attr in range(4):  # 0:"Sales", 1:"CarryOver", 2:"Inventory", 3:"Purchase"
                row = [node.name, attr]
                for week_no in range(output_period):
                    count = len(node.psi4supply[week_no][attr])
                    row.append(count)
                data.append(row)
            for child in node.children:
                collect_data(child, output_period)

        # root_node_outboundのツリー構造を走査してデータを収集
        headers_outbound = ["node_name", "PSI_attribute"] + [f"w{i+1}" for i in range(output_period_outbound)]
        collect_data(self.root_node_outbound, output_period_outbound)

        # データフレームを作成してCSVファイルに保存
        df_outbound = pd.DataFrame(data[:len(data)], columns=headers_outbound)  
        # STOP
        ## 複数のデータフレームを1つに統合する場合
        #df_combined = pd.concat([df_outbound, df_inbound])

        df_outbound.to_csv(save_path, index=False)

        # 完了メッセージを表示
        messagebox.showinfo("CSV Export", f"PSI data has been exported to {save_path}")





    def outbound_lot_by_lot_to_csv(self):
        # ファイル保存ダイアログを表示して保存先ファイルパスを取得
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not save_path:
            return  # ユーザーがキャンセルした場合

        # 計画の出力期間を計算
        output_period_outbound = 53 * self.root_node_outbound.plan_range
        start_year = self.plan_year_st

        # ヘッダーの作成
        headers = ["tier", "node_name", "parent", "PSI_attribute", "year", "week_no", "lot_id"]

        # データの収集
        data = []

        def collect_data(node, output_period, tier_no, parent_name):
            for attr in range(4):  # 0:"Sales", 1:"CarryOver", 2:"Inventory", 3:"Purchase"
                for week_no in range(output_period):
                    year = start_year + week_no // 53
                    week = week_no % 53 + 1
                    lot_ids = node.psi4supply[week_no][attr]
                    if not lot_ids:  # 空リストの場合、空文字を追加
                        lot_ids = [""]
                    for lot_id in lot_ids:
                        data.append([tier_no, node.name, parent_name, attr, year, week, lot_id])
            for child in node.children:
                collect_data(child, output_period, tier_no + 1, node.name)

        # root_node_outboundのツリー構造を走査してデータを収集
        collect_data(self.root_node_outbound, output_period_outbound, 0, "root")

        # データフレームを作成してCSVファイルに保存
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(save_path, index=False)

        # 完了メッセージを表示
        messagebox.showinfo("CSV Export", f"Lot by Lot data has been exported to {save_path}")





    def inbound_psi_to_csv(self):
        # ファイル保存ダイアログを表示して保存先ファイルパスを取得
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not save_path:
            return  # ユーザーがキャンセルした場合

        # 計画の出力期間を計算
        output_period_inbound = 53 * self.root_node_inbound.plan_range

        # データの収集
        data = []

        def collect_data(node, output_period):
            for attr in range(4):  # 0:"Sales", 1:"CarryOver", 2:"Inventory", 3:"Purchase"
                row = [node.name, attr]
                for week_no in range(output_period):
                    count = len(node.psi4supply[week_no][attr])
                    row.append(count)
                data.append(row)
            for child in node.children:
                collect_data(child, output_period)

        # root_node_inboundのツリー構造を走査してデータを収集
        headers_inbound = ["node_name", "PSI_attribute"] + [f"w{i+1}" for i in range(output_period_inbound)]
        collect_data(self.root_node_inbound, output_period_inbound)


        # データフレームを作成してCSVファイルに保存
        df_inbound = pd.DataFrame(data[:len(data)], columns=headers_inbound) 

        df_inbound.to_csv(save_path, index=False)

        # 完了メッセージを表示
        messagebox.showinfo("CSV Export", f"PSI data has been exported to {save_path}")





    def inbound_lot_by_lot_to_csv(self):
        # ファイル保存ダイアログを表示して保存先ファイルパスを取得
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not save_path:
            return  # ユーザーがキャンセルした場合

        # 計画の出力期間を計算
        output_period_inbound = 53 * self.root_node_inbound.plan_range
        start_year = self.plan_year_st

        # ヘッダーの作成
        headers = ["tier", "node_name", "parent", "PSI_attribute", "year", "week_no", "lot_id"]

        # データの収集
        data = []

        def collect_data(node, output_period, tier_no, parent_name):
            for attr in range(4):  # 0:"Sales", 1:"CarryOver", 2:"Inventory", 3:"Purchase"
                for week_no in range(output_period):
                    year = start_year + week_no // 53
                    week = week_no % 53 + 1
                    lot_ids = node.psi4supply[week_no][attr]
                    if not lot_ids:  # 空リストの場合、空文字を追加
                        lot_ids = [""]
                    for lot_id in lot_ids:
                        data.append([tier_no, node.name, parent_name, attr, year, week, lot_id])
            for child in node.children:
                collect_data(child, output_period, tier_no + 1, node.name)

        # root_node_outboundのツリー構造を走査してデータを収集
        collect_data(self.root_node_inbound, output_period_inbound, 0, "root")

        # データフレームを作成してCSVファイルに保存
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(save_path, index=False)

        # 完了メッセージを表示
        messagebox.showinfo("CSV Export", f"Lot by Lot data has been exported to {save_path}")








    def lot_cost_structure_to_csv(self):
        # "PSI for Excel"の処理内容を定義

        # ファイル保存ダイアログを表示して保存先ファイルパスを取得
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not save_path:
            return  # ユーザーがキャンセルした場合

        self.export_cost_structure_to_csv(self.root_node_outbound, self.root_node_inbound, save_path)


        # 完了メッセージを表示
        messagebox.showinfo("CSV Export", f"export_cost_structure_to_csv data has been exported to {save_path}")





    def export_cost_structure_to_csv(self, root_node_outbound, root_node_inbound, file_path):
        attributes = [
            'cs_direct_materials_costs',
            'cs_marketing_promotion',
            'cs_sales_admin_cost',
            'cs_tax_portion',
            'cs_logistics_costs',
            'cs_warehouse_cost',
            'cs_prod_indirect_labor',
            'cs_prod_indirect_others',
            'cs_direct_labor_costs',
            'cs_depreciation_others',
            'cs_profit',
        ]

        def dump_node_amt_all_in(node, node_amt_all):
            for child in node.children:
                dump_node_amt_all_in(child, node_amt_all)
            amt_list = {attr: getattr(node, attr) for attr in attributes}
            if node.name == "JPN":
                node_amt_all["JPN_IN"] = amt_list
            else:
                node_amt_all[node.name] = amt_list
            return node_amt_all

        def dump_node_amt_all_out(node, node_amt_all):
            amt_list = {attr: getattr(node, attr) for attr in attributes}
            if node.name == "JPN":
                node_amt_all["JPN_OUT"] = amt_list
            else:
                node_amt_all[node.name] = amt_list
            for child in node.children:
                dump_node_amt_all_out(child, node_amt_all)
            return node_amt_all

        node_amt_sum_in = dump_node_amt_all_in(root_node_inbound, {})
        node_amt_sum_out = dump_node_amt_all_out(root_node_outbound, {})
        node_amt_sum_in_out = {**node_amt_sum_in, **node_amt_sum_out}

        # 横持ちでデータフレームを作成
        data = []
        for node_name, costs in node_amt_sum_in_out.items():
            row = [node_name] + [costs[attr] for attr in attributes]
            data.append(row)

        df = pd.DataFrame(data, columns=["node_name"] + attributes)

        # CSVファイルにエクスポート
        df.to_csv(file_path, index=False)
        print(f"Cost structure exported to {file_path}")



    def show_cost_structure_bar_graph(self):
        try:
            if self.root_node_outbound is None or self.root_node_inbound is None:
                raise ValueError("Data has not been loaded yet")

            show_nodes_cs_lot_G_Sales_Procure(self.root_node_outbound, self.root_node_inbound)
        
        except ValueError as ve:
            print(f"error: {ve}")
            tk.messagebox.showerror("error", str(ve))
        
        except AttributeError:
            print("Error: Required attributes are missing from the node. Please check if the data is loaded.")
            tk.messagebox.showerror("Error", "Required attributes are missing from the node. Please check if the data is loaded.")
        
        except Exception as e:
            print(f"An unexpected error has occurred: {e}")
            tk.messagebox.showerror("Error", f"An unexpected error has occurred: {e}")

    def show_nodes_cs_lot_G_Sales_Procure(root_node_outbound, root_node_inbound):
        attributes = [
            'cs_direct_materials_costs',
            'cs_marketing_promotion',
            'cs_sales_admin_cost',
            'cs_tax_portion',
            'cs_logistics_costs',
            'cs_warehouse_cost',
            'cs_prod_indirect_labor',
            'cs_prod_indirect_others',
            'cs_direct_labor_costs',
            'cs_depreciation_others',
            'cs_profit',
        ]

        def dump_node_amt_all_in(node, node_amt_all):
            for child in node.children:
                dump_node_amt_all_in(child, node_amt_all)
            amt_list = {attr: getattr(node, attr) for attr in attributes}
            if node.name == "JPN":
                node_amt_all["JPN_IN"] = amt_list
            else:
                node_amt_all[node.name] = amt_list
            return node_amt_all

        def dump_node_amt_all_out(node, node_amt_all):
            amt_list = {attr: getattr(node, attr) for attr in attributes}
            if node.name == "JPN":
                node_amt_all["JPN_OUT"] = amt_list
            else:
                node_amt_all[node.name] = amt_list
            for child in node.children:
                dump_node_amt_all_out(child, node_amt_all)
            return node_amt_all

        node_amt_sum_in = dump_node_amt_all_in(root_node_inbound, {})
        node_amt_sum_out = dump_node_amt_all_out(root_node_outbound, {})
        node_amt_sum_in_out = {**node_amt_sum_in, **node_amt_sum_out}

        print("node_amt_sum_out", node_amt_sum_out)

        make_stack_bar4cost_stracture(node_amt_sum_out)

        # CSVファイルへのエクスポートを呼び出す
        export_cost_structure_to_csv(self, root_node_outbound, root_node_inbound, "cost_structure.csv")




    def outbound_rev_prof_csv(self):
        # "PSI for Excel"の処理内容を定義
        pass



    def supplychain_performance_to_csv(self):
        # ファイル保存ダイアログを表示して保存先ファイルパスを取得
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not save_path:
            return  # ユーザーがキャンセルした場合

        self.export_performance_to_csv(self.root_node_outbound, self.root_node_inbound, save_path)

        # 完了メッセージを表示
        messagebox.showinfo("CSV Export", f"Business performance data has been exported to {save_path}")

    def export_performance_to_csv(self, root_node_outbound, root_node_inbound, file_path):
        attributes = [

            #'eval_revenue',
            #'eval_profit',
            #'eval_PO_cost',
            #'eval_P_cost',
            #'eval_WH_cost',
            #'eval_SGMC',
            #'eval_Dist_Cost'

# evaluated cost = Cost Structure X lot_counts
            #"eval_cs_price_sales_shipped",
            #"eval_cs_cost_total",
            #"eval_cs_profit",
            #"eval_cs_marketing_promotion",
            #"eval_cs_sales_admin_cost",
            #"eval_cs_SGA_total",
            #"eval_cs_custom_tax",
            #"eval_cs_tax_portion",
            #"eval_cs_logistics_costs",
            #"eval_cs_warehouse_cost",
            #"eval_cs_direct_materials_costs",
            #
            #"eval_cs_purchase_total_cost",
            #"eval_cs_prod_indirect_labor",
            #"eval_cs_prod_indirect_others",
            #"eval_cs_direct_labor_costs",
            #"eval_cs_depreciation_others",
            #"eval_cs_manufacturing_overhead"

# evaluated cost = Cost Structure X lot_counts



            "cs_custom_tax",             # political TAX parameter
            #"cs_WH_cost_coefficiet",    # operational cost parameter


            # "purchase_total_cost" is followings
            "cs_direct_materials_costs", # material
            "cs_tax_portion",            # portion calculated by TAX xx%
            "cs_logistics_costs",        # inbound logistic cost

            # plant operations are followings
            "cs_warehouse_cost",

            # eval_cs_manufacturing_overhead
            "cs_prod_indirect_labor",    # man indirect
            "cs_prod_indirect_others",   # expense
            "cs_direct_labor_costs",     # man direct
            "cs_depreciation_others",    # machine

            # Sales side operations
            "cs_marketing_promotion",
            "cs_sales_admin_cost",

            # cash generated
            "cs_profit",

            # sub total cost item
            "cs_purchase_total_cost",    # material + TAX + logi cost
            "cs_manufacturing_overhead",
            "cs_SGA_total",  # marketing_promotion + sales_admin_cost

            "cs_cost_total",
            "cs_price_sales_shipped", # revenue
        ]


        def dump_node_amt_all_in(node, node_amt_all):
            for child in node.children:
                dump_node_amt_all_in(child, node_amt_all)
            amt_list = {attr: getattr(node, attr) for attr in attributes}
            if node.name == "JPN":
                node_amt_all["JPN_IN"] = amt_list
            else:
                node_amt_all[node.name] = amt_list
            return node_amt_all

        def dump_node_amt_all_out(node, node_amt_all):
            amt_list = {attr: getattr(node, attr) for attr in attributes}
            if node.name == "JPN":
                node_amt_all["JPN_OUT"] = amt_list
            else:
                node_amt_all[node.name] = amt_list
            for child in node.children:
                dump_node_amt_all_out(child, node_amt_all)
            return node_amt_all

        node_amt_sum_in = dump_node_amt_all_in(root_node_inbound, {})
        node_amt_sum_out = dump_node_amt_all_out(root_node_outbound, {})
        node_amt_sum_in_out = {**node_amt_sum_in, **node_amt_sum_out}

        # 横持ちでデータフレームを作成
        data = []
        for node_name, performance in node_amt_sum_in_out.items():
            row = [node_name] + [performance[attr] for attr in attributes]
            data.append(row)

        df = pd.DataFrame(data, columns=["node_name"] + attributes)

        # CSVファイルにエクスポート
        df.to_csv(file_path, index=False)
        print(f"Business performance data exported to {file_path}")






    def inbound_cost_structure_to_csv(self):
        # "PSI for Excel"の処理内容を定義
        pass

    def inbound_rev_prof_csv(self):
        # "PSI for Excel"の処理内容を定義
        pass



    def psi_for_excel(self):
        # "PSI for Excel"の処理内容を定義
        pass








    def show_3d_overview(self):
        # CSVファイルを読み込む
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return  # ユーザーがキャンセルした場合

        # CSVファイルを読み込む
        df = pd.read_csv(file_path)

        # TreeViewを作成してノードを選択させる
        tree_window = tk.Toplevel(self.root)
        tree_window.title("Select Node")
        tree = ttk.Treeview(tree_window)
        tree.pack(fill=tk.BOTH, expand=True)

        # ユニークなノード名のリストを抽出
        node_list = df[['tier', 'node_name', 'parent']].drop_duplicates().sort_values(by='tier')

        # ルートノードを追加
        root_node = tree.insert('', 'end', text='root', iid='root')
        node_id_map = {"root": root_node}

        # ノードをツリー構造に追加
        def add_node(parent, tier, node_name, node_id):
            tree.insert(parent, 'end', node_id, text=f"Tier {tier}: {node_name}")

        for _, row in node_list.iterrows():
            node_id = f"{row['tier']}_{row['node_name']}"
            parent_node_name = row.get("parent", "root")
            if parent_node_name in node_id_map:
                parent = node_id_map[parent_node_name]
                add_node(parent, row["tier"], row["node_name"], node_id)
                node_id_map[row["node_name"]] = node_id
            else:
                # 親ノードが見つからない場合はルートノードを使用
                add_node(root_node, row["tier"], row["node_name"], node_id)
                node_id_map[row["node_name"]] = node_id

        # 選択ボタンの設定
        def select_node():
            selected_item = tree.selection()
            if selected_item:
                node_name = tree.item(selected_item[0], "text").split(": ")[1]
                tree_window.destroy()
                self.plot_3d_graph(df, node_name)

        select_button = tk.Button(tree_window, text="Select", command=select_node)
        select_button.pack()




    import tkinter as tk
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    def plot_3d_graph(self, df, node_name):
        psi_attr_map = {0: "lightblue", 1: "darkblue", 2: "brown", 3: "gold"}

        x = []
        y = []
        z = []
        labels = []
        colors = []
        week_no_dict = {}
        max_z_value_lot_id_map = {}

        lot_position_map = {}

        for _, row in df.iterrows():
            if row["node_name"] == node_name and pd.notna(row["lot_id"]):
                x_value = row["PSI_attribute"]
                year = row['year']
                week_no = row['week_no']

                # Calculate week_no_serial
                start_year = df['year'].min()
                week_no_serial = (year - start_year) * 53 + week_no
                week_no_dict[week_no_serial] = f"{year}{str(week_no).zfill(2)}"

                y_value = week_no_serial
                lot_id = row['lot_id']

                if (x_value, y_value) not in lot_position_map:
                    lot_position_map[(x_value, y_value)] = 0

                z_value = lot_position_map[(x_value, y_value)] + 1
                lot_position_map[(x_value, y_value)] = z_value

                # Update max z_value for the corresponding (x_value, y_value)
                if (x_value, y_value) not in max_z_value_lot_id_map or z_value > max_z_value_lot_id_map[(x_value, y_value)][0]:
                    max_z_value_lot_id_map[(x_value, y_value)] = (z_value, lot_id)

                x.append(x_value)
                y.append(y_value)
                z.append(z_value)
                labels.append(lot_id)
                colors.append(psi_attr_map[row["PSI_attribute"]])

        # Tkinterのウィンドウを作成
        plot_window = tk.Toplevel(self.root)
        plot_window.title(f"3D Plot for {node_name}")

        # Figureを作成
        fig = plt.figure(figsize=(16, 12))  # 図のサイズを指定
        ax = fig.add_subplot(111, projection='3d')

        # 3Dプロットの作成
        scatter = ax.scatter(x, y, z, c=colors, s=1, depthshade=True)  # s=1でプロットサイズを小さく設定
        ax.set_xlabel('PSI Attribute')
        ax.set_ylabel('Time (YYYYWW)')
        ax.set_zlabel('Lot ID Position')

        # x軸のラベル設定
        ax.set_xticks(list(psi_attr_map.keys()))
        ax.set_xticklabels(["Sales", "CarryOver", "Inventory", "Purchase"], rotation=45, ha='right')

        # y軸のラベル設定
        y_ticks = [week_no_serial for week_no_serial in week_no_dict.keys() if week_no_serial % 2 != 0]
        y_labels = [week_no_dict[week_no_serial] for week_no_serial in y_ticks]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, rotation=45, ha='right', fontsize=6)  # フォントサイズをさらに小さく設定

        # 各座標に対応するlot_idの表示（z軸の最大値のみ）
        for (x_value, y_value), (z_value, lot_id) in max_z_value_lot_id_map.items():
            ax.text(x_value, y_value, z_value, lot_id, fontsize=4, color='black', ha='center', va='center')

        # FigureをTkinterのCanvasに追加
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Tkinterのメインループを開始
        plot_window.mainloop()

        # プロットをPNGとして保存
        plt.savefig("interactive_plot.png")
        print("Interactive plot saved as interactive_plot.png")








# viewing Cost Stracture / an image of Value Chain
    # viewing Cost Stracture / an image of Value Chain
    def show_cost_stracture_bar_graph(self):
        try:
            if self.root_node_outbound is None or self.root_node_inbound is None:
                raise ValueError("Data has not been loaded yet")
            
            show_nodes_cs_lot_G_Sales_Procure(self.root_node_outbound, self.root_node_inbound)
        
        except ValueError as ve:
            print(f"error: {ve}")
            tk.messagebox.showerror("error", str(ve))
        
        except AttributeError:
            print("Error: Required attributes are missing from the node. Please check if the data is loaded.")
            tk.messagebox.showerror("Error", "Required attributes are missing from the node. Please check if the data is loaded.")
        
        except Exception as e:
            print(f"An unexpected error has occurred: {e}")
            tk.messagebox.showerror("Error", f"An unexpected error has occurred: {e}")





    def show_month_data_csv(self):
        # ディレクトリが設定されているか確認
        if not hasattr(self, 'directory') or not self.directory:
            tk.messagebox.showwarning("Warning", "No selected DATA DIRECTORY")
            return

        new_window = tk.Toplevel()
        new_window.title("S_month_data.csv")

        # *********************
        # adding directory_name
        # *********************
        filename = "S_month_data.csv"
        in_file_path = os.path.join(self.directory, filename)

        # ファイルの存在を確認
        if not os.path.exists(in_file_path):
            tk.messagebox.showwarning("Warning", f"File not found: {in_file_path}")
            return

        treeview = ttk.Treeview(new_window)
        treeview.pack(fill=tk.BOTH, expand=True)

        # CSVファイルを読み込む
        with open(in_file_path, "r") as file:
            reader = csv.reader(file)
            headers = next(reader)
            treeview["columns"] = headers
            for header in headers:
                treeview.heading(header, text=header)
                treeview.column(header, width=100)
            
            for row in reader:
                treeview.insert("", "end", values=row)



# ********************************************************
# end of menu and csv viewer definition
# ********************************************************





    def on_exit(self):
        # 確認ダイアログの表示
        if messagebox.askokcancel("Quit", "Do you really want to exit?"):
            # 全てのスレッドを終了
            for thread in threading.enumerate():
                if thread is not threading.main_thread():
                    thread.join(timeout=1)
    
            #for widget in self.root.winfo_children():
            #    widget.destroy()
    
            #self.root.destroy()
            self.root.quit()




    def initialize_parameters(self):
        # Global Market Potentialの計算と設定
        market_potential = getattr(self, 'market_potential', self.market_potential)  # 初期設定を含む

        self.gmp_entry.delete(0, tk.END)
        self.gmp_entry.insert(0, "{:,}".format(market_potential))  # 3桁毎にカンマ区切りで表示

        # Target Shareの初期値設定（すでにsetup_uiで設定済み）

        # Total Supply Planの計算と設定
        target_share = float(self.ts_entry.get().replace('%', ''))/100  # 文字列を浮動小数点数に変換して%を除去

        total_supply_plan = round(market_potential * target_share)
        self.tsp_entry.delete(0, tk.END)
        self.tsp_entry.insert(0, "{:,}".format(total_supply_plan))  # 3桁毎にカンマ区切りで表示

        #self.global_market_potential  = global_market_potential

        self.market_potential         = market_potential
        self.target_share             = target_share           
        self.total_supply_plan        = total_supply_plan
        print(f"初期化時 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加



    def updated_parameters(self):
        print(f"updated_parameters更新前 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加

        # Market Potentialの計算と設定
        market_potential = self.market_potential
        print("market_potential", market_potential)
        
        self.gmp_entry.delete(0, tk.END)
        self.gmp_entry.insert(0, "{:,}".format(market_potential))  # 3桁毎にカンマ区切りで表示

        # Target Shareの初期値設定（すでにsetup_uiで設定済み）
        #@ ADD: Keep the current target_share value if user has not entered a new value
        if self.ts_entry.get():
            target_share = float(self.ts_entry.get().replace('%', '')) / 100  # 文字列を浮動小数点数に変換して%を除去
        else:
            target_share = self.target_share

        # Total Supply Planの計算と設定
        total_supply_plan = round(market_potential * target_share)
        self.tsp_entry.delete(0, tk.END)
        self.tsp_entry.insert(0, "{:,}".format(total_supply_plan))  # 3桁毎にカンマ区切りで表示

        self.market_potential = market_potential
        self.target_share = target_share
        self.total_supply_plan = total_supply_plan

        print(f"updated_parameters更新時 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加




    def updated_parameters_OLD(self):

        print(f"updated_parameters更新前 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加

        # Market Potentialの計算と設定
        market_potential = getattr(self, 'market_potential', self.market_potential)  # 初期設定を含む

        print("market_potential", market_potential)

        self.gmp_entry.delete(0, tk.END)
        self.gmp_entry.insert(0, "{:,}".format(market_potential))  # 3桁毎にカンマ区切りで表示

        # Target Shareの初期値設定（すでにsetup_uiで設定済み）

        #@ ADD
        target_share = getattr(self, 'target_share', self.target_share)  # 初期設定を含む

        # Total Supply Planの計算と設定
        target_share = float(self.ts_entry.get().replace('%', ''))/100  # 文字列を浮動小数点数に変換して%を除去

        total_supply_plan = round(market_potential * target_share)
        self.tsp_entry.delete(0, tk.END)
        self.tsp_entry.insert(0, "{:,}".format(total_supply_plan))  # 3桁毎にカンマ区切りで表示

        self.market_potential = market_potential
        self.target_share = target_share
        self.total_supply_plan = total_supply_plan

        print(f"updated_parameters更新時 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加






    def update_total_supply_plan(self, event):
        try:
            market_potential = float(self.gmp_entry.get().replace(',', ''))
            target_share = float(self.ts_entry.get().replace('%', ''))/100
        except ValueError:
            print("Invalid input for Global Market Potential or Target Share.")
            return

        # Total Supply Planの再計算
        total_supply_plan = round(market_potential * target_share)

        self.total_supply_plan = total_supply_plan

        # Total Supply Planフィールドの更新
        self.tsp_entry.config(state='normal')
        self.tsp_entry.delete(0, tk.END)
        self.tsp_entry.insert(0, "{:,}".format(total_supply_plan))  # 3桁毎にカンマ区切りで表示
        self.tsp_entry.config(state='normal')






    def optimize_show_network_E2E(root_node_outbound, nodes_outbound, root_node_inbound, nodes_inbound, G, Gdm, Gsp):
        root_node_name_out = root_node_outbound.name  # name
        root_node_name_in = root_node_inbound.name

        # Demand side
        total_demand = 0
        total_demand = set_leaf_demand(root_node_outbound, total_demand)

        print("average_total_demand", total_demand)
        print("root_node_outbound.nx_demand", root_node_outbound.nx_demand)

        root_node_outbound.nx_demand = total_demand
        root_node_inbound.nx_demand = total_demand

        G_add_nodes_from_tree(root_node_outbound, G)
        G_add_nodes_from_tree_skip_root(root_node_inbound, root_node_name_in, G)

        G.add_node("office", demand=total_demand)
        G.add_node(root_node_outbound.name, demand=0)
        G.add_node("procurement_office", demand=(-1 * total_demand))

        print("G.add_node sales_office total_demand=", total_demand)
        print("G.add_node procurement_office total_demand=", (-1 * total_demand))

        G_add_edge_from_tree(root_node_outbound, G)
        supplyers_capacity = root_node_inbound.nx_demand * 2
        G_add_edge_from_inbound_tree(root_node_inbound, supplyers_capacity, G)

        G_add_nodes_from_tree(root_node_outbound, Gdm)
        Gdm.add_node(root_node_outbound.name, demand=(-1 * total_demand))
        Gdm.add_node("office", demand=total_demand)
        Gdm_add_edge_sc2nx_outbound(root_node_outbound, Gdm)

        G_add_nodes_from_tree(root_node_inbound, Gsp)
        Gsp.add_node("procurement_office", demand=(-1 * total_demand))
        Gsp.add_node(root_node_inbound.name, demand=total_demand)
        Gsp_add_edge_sc2nx_inbound(root_node_inbound, Gsp)

        print("ノードの需要とエッジのキャパシティを確認")
        flowCost_dm, flowDict_dm = nx.network_simplex(Gdm)
        flowCost_sp, flowDict_sp = nx.network_simplex(Gsp)

        print("ノードの需要とエッジのキャパシティを確認")
        for node in G.nodes(data=True):
            print(node)
        for edge in G.edges(data=True):
            print(edge)

        print("demandの確認")
        for node, data in G.nodes(data=True):
            print(f"Node: {node}, Demand: {data.get('demand', 0)}")

        pos_E2E = make_E2E_positions(root_node_outbound, root_node_inbound)

        # エッジラベルの設定
        edge_labels_dm = {}
        for (i, j) in Gdm.edges():
            edge_labels_dm[i, j] = f"{Gdm[i][j]['weight']} ({flowDict_dm[i][j]}/{Gdm[i][j]['capacity']})"

        edge_labels_sp = {}
        for (i, j) in Gsp.edges():
            edge_labels_sp[i, j] = f"{Gsp[i][j]['weight']} ({flowDict_sp[i][j]}/{Gsp[i][j]['capacity']})"

        # グラフを描画
        fig, ax = plt.subplots()
    
        # Gdmのエッジ描画
        for (i, j) in Gdm.edges():
            if j != "office":
                x0, y0 = pos_E2E[i]
                x1, y1 = pos_E2E[j]
                ax.annotate(
                    '', xy=(x1, y1), xycoords='data', xytext=(x0, y0), textcoords='data',
                    arrowprops=dict(arrowstyle="->", color="blue", lw=1.0)
                )
                ax.text((x0 + x1) / 2, (y0 + y1) / 2, edge_labels_dm[i, j], fontsize=10, ha='center')

        # Gspのエッジ描画
        for (i, j) in Gsp.edges():
            if i != "procurement_office":
                x0, y0 = pos_E2E[i]
                x1, y1 = pos_E2E[j]
                ax.annotate(
                    '', xy=(x1, y1), xycoords='data', xytext=(x0, y0), textcoords='data',
                    arrowprops=dict(arrowstyle="->", color="green", lw=1.0)
                )
                ax.text((x0 + x1) / 2, (y0 + y1) / 2, edge_labels_sp[i, j], fontsize=10, ha='center')

        # Gのエッジ描画
        for (i, j) in G.edges():
            x0, y0 = pos_E2E[i]
            x1, y1 = pos_E2E[j]
            ax.plot([x0, x1], [y0, y1], 'k-', lw=1)

        # ノードの描画
        for node in G.nodes():
            x, y = pos_E2E[node]
            ax.plot(x, y, 'o', markersize=10, color='lightblue')
            ax.text(x, y, f'{node} (demand: {G.nodes[node]["demand"]})', fontsize=10, ha='center')

        plt.title("End-to-End Network")
        plt.show()






    def eval_supply_chain_cost(self, node):
    
        # *********************
        # counting Purchase Order
        # *********************
        # psi_listのPOは、psi_list[w][3]の中のlot_idのロット数=リスト長
        node.set_lot_counts()
    
    
    
        # *********************
        # EvalPlanSIP()の中でnode instanceに以下をセットする
        # self.profit, self.revenue, self.profit_ratio
        # *********************
    
        # by weekの計画状態xxx[w]の変化を評価して、self.eval_xxxにセット
        total_revenue, total_profit = node.EvalPlanSIP_cost()

    
        self.total_revenue += total_revenue
        self.total_profit  += total_profit
    
    
        #@241118 "eval_" is 1st def /  "eval_cs_" is 2nd def
        # print(
        #    "Eval node profit revenue profit_ratio",
        #    node.name,
        #    node.eval_profit,
        #    node.eval_revenue,
        #    node.eval_profit_ratio,
        # )
    
        for child in node.children:
    
            self.eval_supply_chain_cost(child)
    


    def eval_supply_chain_cost4opt(self, node_opt):
    
        # change from "out_opt" to "outbound"
        node = self.nodes_outbound[node_opt.name]

        # *********************
        # counting Purchase Order
        # *********************
        # psi_listのPOは、psi_list[w][3]の中のlot_idのロット数=リスト長

        # lot_counts is "out_opt"side
        node_opt.set_lot_counts()

        #@ STOP
        #node.set_lot_counts()
    
        # output:
        #    self.lot_counts_all = sum(self.lot_counts)

        # change lot_counts from "out_opt"side to "outbound"side
        node.lot_counts_all = node_opt.lot_counts_all
    
        # *********************
        # EvalPlanSIP()の中でnode instanceに以下をセットする
        # self.profit, self.revenue, self.profit_ratio
        # *********************
    
        # by weekの計画状態xxx[w]の変化を評価して、self.eval_xxxにセット
        total_revenue, total_profit = node.EvalPlanSIP_cost()

    
        #@241225 ADD
        node.total_revenue     = total_revenue    
        node.total_profit      = total_profit     
                                 
        node_opt.total_revenue = total_revenue
        node_opt.total_profit  = total_profit 
                                 
        self.total_revenue += total_revenue
        self.total_profit  += total_profit
    
    
        #@241118 "eval_" is 1st def /  "eval_cs_" is 2nd def
        # print(
        #    "Eval node profit revenue profit_ratio",
        #    node.name,
        #    node.eval_profit,
        #    node.eval_revenue,
        #    node.eval_profit_ratio,
        # )
    
        for child in node.children:
    
            self.eval_supply_chain_cost4opt(child)





    def update_evaluation_results(self):


        # Evaluation on PSI
        self.total_revenue = 0
        self.total_profit  = 0
        self.profit_ratio  = 0


        # ***********************
        # This is a simple Evaluation process with "cost table"
        # ***********************


#@241120 STOP
#        self.eval_plan()
#
#    def eval_plan(self):



        # 在庫係数の計算
        # I_cost_coeff = I_total_qty_init / I_total_qty_planned
        #
        # 計画された在庫コストの算定
        # I_cost_planned = I_cost_init * I_cost_coeff
    
    
        # by node evaluation Revenue / Cost / Profit
        # "eval_xxx" = "lot_counts" X "cs_xxx" that is from cost_table
        # Inventory cost has 係数 = I_total on Demand/ I_total on Supply
    
    
        #self.total_revenue = 0
        #self.total_profit  = 0
    
        self.eval_supply_chain_cost(self.root_node_outbound)
    
        self.eval_supply_chain_cost(self.root_node_inbound)









        ttl_revenue = self.total_revenue
        ttl_profit  = self.total_profit

        if ttl_revenue == 0:
            ttl_profit_ratio = 0
        else:
            ttl_profit_ratio = ttl_profit / ttl_revenue

        # 四捨五入して表示 
        total_revenue = round(ttl_revenue) 
        total_profit = round(ttl_profit) 
        profit_ratio = round(ttl_profit_ratio*100, 1) # パーセント表示

        print("total_revenue", total_revenue)
        print("total_profit", total_profit)
        print("profit_ratio", profit_ratio)


#total_revenue 343587
#total_profit 32205
#profit_ratio 9.4


        self.total_revenue_entry.config(state='normal')
        self.total_revenue_entry.delete(0, tk.END)
        self.total_revenue_entry.insert(0, f"{total_revenue:,}")
        #self.total_revenue_entry.insert(0, str(kpi_results["total_revenue"]))
        self.total_revenue_entry.config(state='readonly')


        self.total_profit_entry.config(state='normal')
        self.total_profit_entry.delete(0, tk.END)
        self.total_profit_entry.insert(0, f"{total_profit:,}")
        #self.total_profit_entry.insert(0, str(kpi_results["total_profit"]))
        self.total_profit_entry.config(state='readonly')


        self.profit_ratio_entry.config(state='normal')
        self.profit_ratio_entry.delete(0, tk.END)
        self.profit_ratio_entry.insert(0, f"{profit_ratio}%")
        self.profit_ratio_entry.config(state='readonly')

        # 画面を再描画
        self.total_revenue_entry.update_idletasks()
        self.total_profit_entry.update_idletasks()
        self.profit_ratio_entry.update_idletasks()





    def update_evaluation_results4optimize(self):


        # Evaluation on PSI
        self.total_revenue = 0
        self.total_profit  = 0
        self.profit_ratio  = 0


        # ***********************
        # This is a simple Evaluation process with "cost table"
        # ***********************


        # 在庫係数の計算
        # I_cost_coeff = I_total_qty_init / I_total_qty_planned
        #
        # 計画された在庫コストの算定
        # I_cost_planned = I_cost_init * I_cost_coeff
    
    
        # by node evaluation Revenue / Cost / Profit
        # "eval_xxx" = "lot_counts" X "cs_xxx" that is from cost_table
        # Inventory cost has 係数 = I_total on Demand/ I_total on Supply
    
    
        #self.total_revenue = 0
        #self.total_profit  = 0
    


        #@241225 memo "root_node_out_opt"のtreeにはcs_xxxxがセットされていない
        # cs_xxxxのあるnode = self.nodes_outbound[node_opt.name]に変換して参照
        #@241225 be checkek
        # ***************************
        # change ROOT HANDLE
        # ***************************
        self.eval_supply_chain_cost4opt(self.root_node_out_opt)

        print("self.root_node_out_opt.name", self.root_node_out_opt.name)

        #self.eval_supply_chain_cost(self.root_node_outbound)
        #self.eval_supply_chain_cost(self.root_node_inbound)

        ttl_revenue = self.total_revenue
        ttl_profit  = self.total_profit

        print("def update_evaluation_results4optimize")
        print("self.total_revenue", self.total_revenue)
        print("self.total_profit" , self.total_profit)


        if ttl_revenue == 0:
            ttl_profit_ratio = 0
        else:
            ttl_profit_ratio = ttl_profit / ttl_revenue

        # 四捨五入して表示 
        total_revenue = round(ttl_revenue) 
        total_profit = round(ttl_profit) 
        profit_ratio = round(ttl_profit_ratio*100, 1) # パーセント表示

        print("total_revenue", total_revenue)
        print("total_profit", total_profit)
        print("profit_ratio", profit_ratio)


#total_revenue 343587
#total_profit 32205
#profit_ratio 9.4


        self.total_revenue_entry.config(state='normal')
        self.total_revenue_entry.delete(0, tk.END)
        self.total_revenue_entry.insert(0, f"{total_revenue:,}")
        #self.total_revenue_entry.insert(0, str(kpi_results["total_revenue"]))
        self.total_revenue_entry.config(state='readonly')


        self.total_profit_entry.config(state='normal')
        self.total_profit_entry.delete(0, tk.END)
        self.total_profit_entry.insert(0, f"{total_profit:,}")
        #self.total_profit_entry.insert(0, str(kpi_results["total_profit"]))
        self.total_profit_entry.config(state='readonly')


        self.profit_ratio_entry.config(state='normal')
        self.profit_ratio_entry.delete(0, tk.END)
        self.profit_ratio_entry.insert(0, f"{profit_ratio}%")
        self.profit_ratio_entry.config(state='readonly')

        # 画面を再描画
        self.total_revenue_entry.update_idletasks()
        self.total_profit_entry.update_idletasks()
        self.profit_ratio_entry.update_idletasks()


# ******************************
# actions
# ******************************


    def load_data_files(self):

        directory = filedialog.askdirectory(title="Select Data Directory")

        if directory:

            # ***********************
            # Lot sizeを取得して変換
            # ***********************
            #try:
            #    self.lot_size = int(self.lot_size_entry.get())
            #except ValueError:
            #    print("Invalid lot size input. Using default value.")

            # Lot size, Plan Year Start, and Plan Rangeを取得して変換
            try:
                self.lot_size = int(self.lot_size_entry.get())
                self.plan_year_st = int(self.plan_year_entry.get())
                self.plan_range = int(self.plan_range_entry.get())
            except ValueError:
                print("Invalid input for lot size, plan year start, or plan range. Using default values.")

            self.outbound_data = []
            self.inbound_data = []

            print("os.listdir(directory)",os.listdir(directory))

            data_file_list = os.listdir(directory)


            # save directory
            self.directory = directory
            self.load_directory = directory


            # ************************
            # read "profile_tree_outbound.csv"
            # build tree_outbound
            # ************************
            if "profile_tree_outbound.csv" in data_file_list:

                filename = "profile_tree_outbound.csv"

                file_path = os.path.join(directory, filename)
                #filepath = os.path.join(directory, filename)


                #load_outbound(outbound_tree_file)


                # ***************************
                # set file name for "profile tree"
                # ***************************
                #outbound_tree_file = "profile_tree_outbound.csv"
                #inbound_tree_file = "profile_tree_inbound.csv"

                # ***************************
                # create supply chain tree for "out"bound
                # ***************************

                # because of the python interpreter performance point of view,
                # this "create tree" code be placed in here, main process

            #@240830
            # "nodes_xxxx" is dictionary to get "node pointer" from "node name"
                nodes_outbound = {}
                nodes_outbound, root_node_name_out = create_tree_set_attribute(file_path)
                root_node_outbound = nodes_outbound[root_node_name_out]



                def make_leaf_nodes(node, list):
                    if node.children == []: # leaf_nodeの場合
                        list.append(node.name)
                    else:
                        pass

                    for child in node.children:
                        make_leaf_nodes(child, list)

                    return list

                leaf_nodes_out = []
                leaf_nodes_out = make_leaf_nodes(root_node_outbound, leaf_nodes_out)



                # making balance for nodes



                # ********************************
                # set outbound tree handle
                # ********************************
                self.nodes_outbound = nodes_outbound
                self.root_node_outbound = root_node_outbound


                print("leaf_nodes_out", leaf_nodes_out)
                self.leaf_nodes_out = leaf_nodes_out

                # ********************************
                # tree wideth/depth count and adjust
                # ********************************
                set_positions(root_node_outbound)



                # root_node_outbound = nodes_outbound['JPN']      # for test, direct define
                # root_node_outbound = nodes_outbound['JPN_OUT']  # for test, direct define

                # setting parent on its child
                set_parent_all(root_node_outbound)
                print_parent_all(root_node_outbound)

            else:
                print("error: profile_tree_outbound.csv is missed")
                pass


            # ************************
            # read "profile_tree_inbound.csv"
            # build tree_inbound
            # ************************
            if "profile_tree_inbound.csv" in data_file_list:

                filename = "profile_tree_inbound.csv"
                file_path = os.path.join(directory, filename)


                # ***************************
                # create supply chain tree for "in"bound
                # ***************************
                nodes_inbound = {}

                nodes_inbound, root_node_name_in = create_tree_set_attribute(file_path)
                root_node_inbound = nodes_inbound[root_node_name_in]


                # ********************************
                # set inbound tree handle
                # ********************************
                self.nodes_inbound = nodes_inbound
                self.root_node_inbound = root_node_inbound


                # ********************************
                # tree wideth/depth count and adjust
                # ********************************
                set_positions(root_node_inbound)

                # setting parent on its child
                set_parent_all(root_node_inbound)
                print_parent_all(root_node_inbound)

            else:
                print("error: profile_tree_inbound.csv is missed")

                pass




            # ************************
            # read "node_cost_table_outbound.csv"
            # read_set_cost
            # ************************
            if "node_cost_table_outbound.csv" in data_file_list:

                filename = "node_cost_table_outbound.csv"
                file_path = os.path.join(directory, filename)

                read_set_cost(file_path, nodes_outbound)

            else:
                print("error: node_cost_table_outbound.csv is missed")

                pass




            # ************************
            # read "node_cost_table_inbound.csv"
            # read_set_cost
            # ************************
            if "node_cost_table_inbound.csv" in data_file_list:

                filename = "node_cost_table_inbound.csv"
                file_path = os.path.join(directory, filename)

                read_set_cost(file_path, nodes_inbound)


            else:
                print("error: node_cost_table_inbound.csv is missed")

                pass









            # ***************************
            # make price chain table
            # ***************************

            # すべてのパスを見つける
            paths = find_paths(root_node_outbound)

            # 各リストをタプルに変換してsetに変換し、重複を排除
            unique_paths = list(set(tuple(x) for x in paths))

            # タプルをリストに戻す
            unique_paths = [list(x) for x in unique_paths]

            print("")
            print("")

            for path in unique_paths:
                print(path)

            sorted_paths = sorted(paths, key=len)

            print("")
            print("")

            for path in sorted_paths:
                print(path)



            # ************************
            # read "S_month_data.csv"
            # trans_month2week2lot_id_list
            # ************************
            if "S_month_data.csv" in data_file_list:

                filename = "S_month_data.csv"
                in_file_path = os.path.join(directory, filename)


                print("self.lot_size",self.lot_size)

                # 使用例
                #in_file = "S_month_data.csv"
                df_weekly, plan_range, plan_year_st = trans_month2week2lot_id_list(in_file_path, self.lot_size)

                print("plan_year_st",plan_year_st)
                print("plan_range",plan_range)

                # update plan_year_st plan_range
                self.plan_year_st = plan_year_st  # S_monthで更新
                self.plan_range   = plan_range    # S_monthで更新


                # Update the GUI fields
                self.plan_year_entry.delete(0, tk.END)
                self.plan_year_entry.insert(0, str(self.plan_year_st))
                self.plan_range_entry.delete(0, tk.END)
                self.plan_range_entry.insert(0, str(self.plan_range))


                out_file = "S_iso_week_data.csv"
                out_file_path = os.path.join(directory, out_file)

                df_weekly.to_csv(out_file_path, index=False)

                df_capa_year = make_capa_year_month(in_file_path)

                #@241112 test
                year_st = df_capa_year["year"].min()
                year_end = df_capa_year["year"].max()
                print("year_st, year_end",year_st, year_end)

            else:
                print("error: S_month_data.csv is missed")

                pass


            #@241124 ココは、初期のEVAL処理用パラメータ。現在は使用していない
            # planning parameterをNode method(=self.)でセットする。
            # plan_range, lot_counts, cash_in, cash_out用のparameterをセット

            root_node_outbound.set_plan_range_lot_counts(plan_range, plan_year_st)
            root_node_inbound.set_plan_range_lot_counts(plan_range, plan_year_st)

            # ***************************
            # an image of data
            #
            # for node_val in node_yyyyww_value:
            #   #print( node_val )
            #
            ##['SHA_N', 22.580645161290324, 22.580645161290324, 22.580645161290324, 22.5    80645161290324, 26.22914349276974, 28.96551724137931, 28.96551724137931, 28.    96551724137931, 31.067853170189103, 33.87096774193549, 33.87096774193549, 33    .87096774193549, 33.87096774193549, 30.33333333333333, 30.33333333333333, 30    .33333333333333, 30.33333333333333, 31.247311827956988, 31.612903225806452,

            # node_yyyyww_key [['CAN', 'CAN202401', 'CAN202402', 'CAN202403', 'CAN20240    4', 'CAN202405', 'CAN202406', 'CAN202407', 'CAN202408', 'CAN202409', 'CAN202    410', 'CAN202411', 'CAN202412', 'CAN202413', 'CAN202414', 'CAN202415', 'CAN2    02416', 'CAN202417', 'CAN202418', 'CAN202419',

            # ********************************
            # make_node_psi_dict
            # ********************************
            # 1. treeを生成して、nodes[node_name]辞書で、各nodeのinstanceを操作        する
            # 2. 週次S yyyywwの値valueを月次Sから変換、
            #    週次のlotの数Slotとlot_keyを生成、
            # 3. ロット単位=lot_idとするリストSlot_id_listを生成しながらpsi_list        生成
            # 4. node_psi_dict=[node1: psi_list1,,,]を生成、treeのnode.psi4deman        dに接続する
        
            S_week = []
        
            # *************************************************
            # node_psi辞書を初期セットする
            # initialise node_psi_dict
            # *************************************************
            node_psi_dict = {}  # 変数 node_psi辞書
        
            # ***************************
            # outbound psi_dic
            # ***************************
            node_psi_dict_Ot4Dm = {}  # node_psi辞書Outbound4Demand plan
            node_psi_dict_Ot4Sp = {}  # node_psi辞書Outbound4Supply plan
        
            # coupling psi
            node_psi_dict_Ot4Cl = {}  # node_psi辞書Outbound4Couple plan

            # accume psi
            node_psi_dict_Ot4Ac = {}  # node_psi辞書Outbound4Accume plan
        
            # ***************************
            # inbound psi_dic
            # ***************************
            node_psi_dict_In4Dm = {}  # node_psi辞書Inbound4demand plan
            node_psi_dict_In4Sp = {}  # node_psi辞書Inbound4supply plan
        
            # coupling psi
            node_psi_dict_In4Cl = {}  # node_psi辞書Inbound4couple plan
        
            # accume psi
            node_psi_dict_In4Ac = {}  # node_psi辞書Inbound4accume plan

            # ***************************
            # rootからtree nodeをpreorder順に検索 node_psi辞書に空リストをセット        する
            # psi_list = [[[] for j in range(4)] for w in range(53 * plan_range)        ]
            # ***************************
            node_psi_dict_Ot4Dm = make_psi_space_dict(
        root_node_outbound, node_psi_dict_Ot4Dm, plan_range
            )
            node_psi_dict_Ot4Sp = make_psi_space_dict(
                root_node_outbound, node_psi_dict_Ot4Sp, plan_range
            )
            node_psi_dict_Ot4Cl = make_psi_space_dict(
                root_node_outbound, node_psi_dict_Ot4Cl, plan_range
            )
            node_psi_dict_Ot4Ac = make_psi_space_dict(
                root_node_outbound, node_psi_dict_Ot4Ac, plan_range
            )
        
            node_psi_dict_In4Dm = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Dm, plan_range
            )
            node_psi_dict_In4Sp = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Sp, plan_range
            )
            node_psi_dict_In4Cl = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Cl, plan_range
            )
            node_psi_dict_In4Ac = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Ac, plan_range
            )
        
            # ***********************************
            # set_dict2tree
            # ***********************************
            # rootからtreeをpreorder順に検索
            # node_psi辞書内のpsi_list pointerをNodeのnode objectにsetattr()で接        続
        
            set_dict2tree_psi(root_node_outbound, "psi4demand", node_psi_dict_Ot4Dm)
            set_dict2tree_psi(root_node_outbound, "psi4supply", node_psi_dict_Ot4Sp)
            set_dict2tree_psi(root_node_outbound, "psi4couple", node_psi_dict_Ot4Cl)
            set_dict2tree_psi(root_node_outbound, "psi4accume", node_psi_dict_Ot4Ac)
        
            set_dict2tree_psi(root_node_inbound, "psi4demand", node_psi_dict_In4Dm)
            set_dict2tree_psi(root_node_inbound, "psi4supply", node_psi_dict_In4Sp)
            set_dict2tree_psi(root_node_inbound, "psi4couple", node_psi_dict_In4Cl)
            set_dict2tree_psi(root_node_inbound, "psi4accume", node_psi_dict_In4Ac)
        









            # ************************************
            # setting S on PSI
            # ************************************

            # Weekly Lot: CPU:Common Planning UnitをPSI spaceにセットする
            set_df_Slots2psi4demand(root_node_outbound, df_weekly)



            #@241124 adding for "global market potential"
            # ************************************
            # counting all lots
            # ************************************

            #print("check lots on psi4demand[w][0] ")

            ## count lot on all nodes  from  node.psi4demand[w][0] 
            #lot_num = count_lot_all_nodes(root_node_outbound)

            # year_st
            # year_end

            # **************************************
            # count_lots_on_S_psi4demand
            # **************************************
            # psi4demand[w][0]の配置されたSのlots数を年別にcountしてlist化


            def count_lots_on_S_psi4demand(node, S_list):
                if node.children == []:
                    for w_psi in node.psi4demand:
                        S_list.append(w_psi[0])
                for child in node.children:
                    count_lots_on_S_psi4demand(child, S_list)
                return S_list

            S_list = []
            year_lots_list4S = []
            S_list = count_lots_on_S_psi4demand(root_node_outbound, S_list)
            plan_year_st = year_st
            
            for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):
                year_lots4S = count_lots_yyyy(S_list, str(yyyy))
                year_lots_list4S.append(year_lots4S)
            
            # 値をインスタンス変数に保存
            self.market_potential = year_lots_list4S[1]  

            print("self.market_potential", self.market_potential)

            self.total_supply_plan = round(self.market_potential * self.target_share)

            #self.total_supply_plan = self.market_potential
            print("self.total_supply_plan", self.total_supply_plan)



        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                filepath = os.path.join(directory, filename)
                print(f"Loading file: {filename}")
                if "outbound" in filename.lower():
                    self.outbound_data.append(pd.read_csv(filepath))
                elif "inbound" in filename.lower():
                    self.inbound_data.append(pd.read_csv(filepath))
        print("Outbound files loaded.")
        print("Inbound files loaded.")



        # cost_standard_flag = 100のノードを特定する関数
        def find_node_with_cost_standard_flag(nodes, flag_value):
            for node_name, node in nodes.items():
                if node.cost_standard_flag == flag_value:
                    return node_name, node
            return None, None

        # cost_standard_flag = 100のノードを見つける
        # ノードが見つかった場合、base_leafを設定
        node_name, base_leaf = find_node_with_cost_standard_flag(nodes_outbound, 100)

        self.base_leaf_name = node_name

        if node_name == None:
            print("NO cost_stantdard = 100 in profile")
        else:
            print(f"Node name: {node_name}, Base leaf: {base_leaf}")



        root_price = set_price_leaf2root(base_leaf, self.root_node_outbound, 100)
        print("root_price", root_price)
        set_value_chain_outbound(root_price, self.root_node_outbound)
        

        #@241209 ADD decouple_node clearing
        self.decouple_node_selected = []
        self.view_nx_matlib()



        self.root.after(1000, self.show_psi_graph)


        #@241222@ STOP RUN STOP
        # パラメータの初期化と更新を呼び出し
        print("load_data_files is processing")
        self.initialize_parameters()











    def load_data_files4LOADSAVE(self):

        directory = filedialog.askdirectory(title="Select Data Directory")

        if directory:

            # ***********************
            # Lot sizeを取得して変換
            # ***********************
            #try:
            #    self.lot_size = int(self.lot_size_entry.get())
            #except ValueError:
            #    print("Invalid lot size input. Using default value.")

            # Lot size, Plan Year Start, and Plan Rangeを取得して変換
            try:
                self.lot_size = int(self.lot_size_entry.get())
                self.plan_year_st = int(self.plan_year_entry.get())
                self.plan_range = int(self.plan_range_entry.get())
            except ValueError:
                print("Invalid input for lot size, plan year start, or plan range. Using default values.")

            self.outbound_data = []
            self.inbound_data = []

            print("os.listdir(directory)",os.listdir(directory))

            data_file_list = os.listdir(directory)


            # save directory
            self.directory = directory
            self.load_directory = directory


            # ************************
            # read "profile_tree_outbound.csv"
            # build tree_outbound
            # ************************
            if "profile_tree_outbound.csv" in data_file_list:

                filename = "profile_tree_outbound.csv"

                file_path = os.path.join(directory, filename)
                #filepath = os.path.join(directory, filename)


                #load_outbound(outbound_tree_file)


                # ***************************
                # set file name for "profile tree"
                # ***************************
                #outbound_tree_file = "profile_tree_outbound.csv"
                #inbound_tree_file = "profile_tree_inbound.csv"

                # ***************************
                # create supply chain tree for "out"bound
                # ***************************

                # because of the python interpreter performance point of view,
                # this "create tree" code be placed in here, main process

            #@240830
            # "nodes_xxxx" is dictionary to get "node pointer" from "node name"
                nodes_outbound = {}
                nodes_outbound, root_node_name_out = create_tree_set_attribute(file_path)
                root_node_outbound = nodes_outbound[root_node_name_out]



                def make_leaf_nodes(node, list):
                    if node.children == []: # leaf_nodeの場合
                        list.append(node.name)
                    else:
                        pass

                    for child in node.children:
                        make_leaf_nodes(child, list)

                    return list

                leaf_nodes_out = []
                leaf_nodes_out = make_leaf_nodes(root_node_outbound, leaf_nodes_out)



                # making balance for nodes



                # ********************************
                # set outbound tree handle
                # ********************************
                self.nodes_outbound = nodes_outbound
                self.root_node_outbound = root_node_outbound


                print("leaf_nodes_out", leaf_nodes_out)
                self.leaf_nodes_out = leaf_nodes_out

                # ********************************
                # tree wideth/depth count and adjust
                # ********************************
                set_positions(root_node_outbound)



                # root_node_outbound = nodes_outbound['JPN']      # for test, direct define
                # root_node_outbound = nodes_outbound['JPN_OUT']  # for test, direct define

                # setting parent on its child
                set_parent_all(root_node_outbound)
                print_parent_all(root_node_outbound)

            else:
                print("error: profile_tree_outbound.csv is missed")
                pass


            # ************************
            # read "profile_tree_inbound.csv"
            # build tree_inbound
            # ************************
            if "profile_tree_inbound.csv" in data_file_list:

                filename = "profile_tree_inbound.csv"
                file_path = os.path.join(directory, filename)


                # ***************************
                # create supply chain tree for "in"bound
                # ***************************
                nodes_inbound = {}

                nodes_inbound, root_node_name_in = create_tree_set_attribute(file_path)
                root_node_inbound = nodes_inbound[root_node_name_in]


                # ********************************
                # set inbound tree handle
                # ********************************
                self.nodes_inbound = nodes_inbound
                self.root_node_inbound = root_node_inbound


                # ********************************
                # tree wideth/depth count and adjust
                # ********************************
                set_positions(root_node_inbound)

                # setting parent on its child
                set_parent_all(root_node_inbound)
                print_parent_all(root_node_inbound)

            else:
                print("error: profile_tree_inbound.csv is missed")

                pass




            # ************************
            # read "node_cost_table_outbound.csv"
            # read_set_cost
            # ************************
            if "node_cost_table_outbound.csv" in data_file_list:

                filename = "node_cost_table_outbound.csv"
                file_path = os.path.join(directory, filename)

                read_set_cost(file_path, nodes_outbound)

            else:
                print("error: node_cost_table_outbound.csv is missed")

                pass




            # ************************
            # read "node_cost_table_inbound.csv"
            # read_set_cost
            # ************************
            if "node_cost_table_inbound.csv" in data_file_list:

                filename = "node_cost_table_inbound.csv"
                file_path = os.path.join(directory, filename)

                read_set_cost(file_path, nodes_inbound)


            else:
                print("error: node_cost_table_inbound.csv is missed")

                pass









            # ***************************
            # make price chain table
            # ***************************

            # すべてのパスを見つける
            paths = find_paths(root_node_outbound)

            # 各リストをタプルに変換してsetに変換し、重複を排除
            unique_paths = list(set(tuple(x) for x in paths))

            # タプルをリストに戻す
            unique_paths = [list(x) for x in unique_paths]

            print("")
            print("")

            for path in unique_paths:
                print(path)

            sorted_paths = sorted(paths, key=len)

            print("")
            print("")

            for path in sorted_paths:
                print(path)



            # ************************
            # read "S_month_data.csv"
            # trans_month2week2lot_id_list
            # ************************
            if "S_month_data.csv" in data_file_list:

                filename = "S_month_data.csv"
                in_file_path = os.path.join(directory, filename)


                print("self.lot_size",self.lot_size)

                # 使用例
                #in_file = "S_month_data.csv"
                df_weekly, plan_range, plan_year_st = trans_month2week2lot_id_list(in_file_path, self.lot_size)

                print("plan_year_st",plan_year_st)
                print("plan_range",plan_range)

                # update plan_year_st plan_range
                self.plan_year_st = plan_year_st  # S_monthで更新
                self.plan_range   = plan_range    # S_monthで更新


                # Update the GUI fields
                self.plan_year_entry.delete(0, tk.END)
                self.plan_year_entry.insert(0, str(self.plan_year_st))
                self.plan_range_entry.delete(0, tk.END)
                self.plan_range_entry.insert(0, str(self.plan_range))


                out_file = "S_iso_week_data.csv"
                out_file_path = os.path.join(directory, out_file)

                df_weekly.to_csv(out_file_path, index=False)

                df_capa_year = make_capa_year_month(in_file_path)

                #@241112 test
                year_st = df_capa_year["year"].min()
                year_end = df_capa_year["year"].max()
                print("year_st, year_end",year_st, year_end)

            else:
                print("error: S_month_data.csv is missed")

                pass


            #@241124 ココは、初期のEVAL処理用パラメータ。現在は使用していない
            # planning parameterをNode method(=self.)でセットする。
            # plan_range, lot_counts, cash_in, cash_out用のparameterをセット

            root_node_outbound.set_plan_range_lot_counts(plan_range, plan_year_st)
            root_node_inbound.set_plan_range_lot_counts(plan_range, plan_year_st)

            # ***************************
            # an image of data
            #
            # for node_val in node_yyyyww_value:
            #   #print( node_val )
            #
            ##['SHA_N', 22.580645161290324, 22.580645161290324, 22.580645161290324, 22.5    80645161290324, 26.22914349276974, 28.96551724137931, 28.96551724137931, 28.    96551724137931, 31.067853170189103, 33.87096774193549, 33.87096774193549, 33    .87096774193549, 33.87096774193549, 30.33333333333333, 30.33333333333333, 30    .33333333333333, 30.33333333333333, 31.247311827956988, 31.612903225806452,

            # node_yyyyww_key [['CAN', 'CAN202401', 'CAN202402', 'CAN202403', 'CAN20240    4', 'CAN202405', 'CAN202406', 'CAN202407', 'CAN202408', 'CAN202409', 'CAN202    410', 'CAN202411', 'CAN202412', 'CAN202413', 'CAN202414', 'CAN202415', 'CAN2    02416', 'CAN202417', 'CAN202418', 'CAN202419',

            # ********************************
            # make_node_psi_dict
            # ********************************
            # 1. treeを生成して、nodes[node_name]辞書で、各nodeのinstanceを操作        する
            # 2. 週次S yyyywwの値valueを月次Sから変換、
            #    週次のlotの数Slotとlot_keyを生成、
            # 3. ロット単位=lot_idとするリストSlot_id_listを生成しながらpsi_list        生成
            # 4. node_psi_dict=[node1: psi_list1,,,]を生成、treeのnode.psi4deman        dに接続する
        
            S_week = []
        
            # *************************************************
            # node_psi辞書を初期セットする
            # initialise node_psi_dict
            # *************************************************
            node_psi_dict = {}  # 変数 node_psi辞書
        
            # ***************************
            # outbound psi_dic
            # ***************************
            node_psi_dict_Ot4Dm = {}  # node_psi辞書Outbound4Demand plan
            node_psi_dict_Ot4Sp = {}  # node_psi辞書Outbound4Supply plan
        
            # coupling psi
            node_psi_dict_Ot4Cl = {}  # node_psi辞書Outbound4Couple plan

            # accume psi
            node_psi_dict_Ot4Ac = {}  # node_psi辞書Outbound4Accume plan
        
            # ***************************
            # inbound psi_dic
            # ***************************
            node_psi_dict_In4Dm = {}  # node_psi辞書Inbound4demand plan
            node_psi_dict_In4Sp = {}  # node_psi辞書Inbound4supply plan
        
            # coupling psi
            node_psi_dict_In4Cl = {}  # node_psi辞書Inbound4couple plan
        
            # accume psi
            node_psi_dict_In4Ac = {}  # node_psi辞書Inbound4accume plan

            # ***************************
            # rootからtree nodeをpreorder順に検索 node_psi辞書に空リストをセット        する
            # psi_list = [[[] for j in range(4)] for w in range(53 * plan_range)        ]
            # ***************************
            node_psi_dict_Ot4Dm = make_psi_space_dict(
        root_node_outbound, node_psi_dict_Ot4Dm, plan_range
            )
            node_psi_dict_Ot4Sp = make_psi_space_dict(
                root_node_outbound, node_psi_dict_Ot4Sp, plan_range
            )
            node_psi_dict_Ot4Cl = make_psi_space_dict(
                root_node_outbound, node_psi_dict_Ot4Cl, plan_range
            )
            node_psi_dict_Ot4Ac = make_psi_space_dict(
                root_node_outbound, node_psi_dict_Ot4Ac, plan_range
            )
        
            node_psi_dict_In4Dm = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Dm, plan_range
            )
            node_psi_dict_In4Sp = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Sp, plan_range
            )
            node_psi_dict_In4Cl = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Cl, plan_range
            )
            node_psi_dict_In4Ac = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Ac, plan_range
            )
        
            # ***********************************
            # set_dict2tree
            # ***********************************
            # rootからtreeをpreorder順に検索
            # node_psi辞書内のpsi_list pointerをNodeのnode objectにsetattr()で接        続
        
            set_dict2tree_psi(root_node_outbound, "psi4demand", node_psi_dict_Ot4Dm)
            set_dict2tree_psi(root_node_outbound, "psi4supply", node_psi_dict_Ot4Sp)
            set_dict2tree_psi(root_node_outbound, "psi4couple", node_psi_dict_Ot4Cl)
            set_dict2tree_psi(root_node_outbound, "psi4accume", node_psi_dict_Ot4Ac)
        
            set_dict2tree_psi(root_node_inbound, "psi4demand", node_psi_dict_In4Dm)
            set_dict2tree_psi(root_node_inbound, "psi4supply", node_psi_dict_In4Sp)
            set_dict2tree_psi(root_node_inbound, "psi4couple", node_psi_dict_In4Cl)
            set_dict2tree_psi(root_node_inbound, "psi4accume", node_psi_dict_In4Ac)
        









            # ************************************
            # setting S on PSI
            # ************************************

            # Weekly Lot: CPU:Common Planning UnitをPSI spaceにセットする
            set_df_Slots2psi4demand(root_node_outbound, df_weekly)



            #@241124 adding for "global market potential"
            # ************************************
            # counting all lots
            # ************************************

            #print("check lots on psi4demand[w][0] ")

            ## count lot on all nodes  from  node.psi4demand[w][0] 
            #lot_num = count_lot_all_nodes(root_node_outbound)

            # year_st
            # year_end

            # **************************************
            # count_lots_on_S_psi4demand
            # **************************************
            # psi4demand[w][0]の配置されたSのlots数を年別にcountしてlist化


            def count_lots_on_S_psi4demand(node, S_list):
                if node.children == []:
                    for w_psi in node.psi4demand:
                        S_list.append(w_psi[0])
                for child in node.children:
                    count_lots_on_S_psi4demand(child, S_list)
                return S_list

            S_list = []
            year_lots_list4S = []
            S_list = count_lots_on_S_psi4demand(root_node_outbound, S_list)
            plan_year_st = year_st
            
            for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):
                year_lots4S = count_lots_yyyy(S_list, str(yyyy))
                year_lots_list4S.append(year_lots4S)
            
            # 値をインスタンス変数に保存
            self.market_potential = year_lots_list4S[1]  

            print("self.market_potential", self.market_potential)

            self.total_supply_plan = round(self.market_potential * self.target_share)

            #self.total_supply_plan = self.market_potential
            print("self.total_supply_plan", self.total_supply_plan)



        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                filepath = os.path.join(directory, filename)
                print(f"Loading file: {filename}")
                if "outbound" in filename.lower():
                    self.outbound_data.append(pd.read_csv(filepath))
                elif "inbound" in filename.lower():
                    self.inbound_data.append(pd.read_csv(filepath))
        print("Outbound files loaded.")
        print("Inbound files loaded.")



        # cost_standard_flag = 100のノードを特定する関数
        def find_node_with_cost_standard_flag(nodes, flag_value):
            for node_name, node in nodes.items():
                if node.cost_standard_flag == flag_value:
                    return node_name, node
            return None, None

        # cost_standard_flag = 100のノードを見つける
        # ノードが見つかった場合、base_leafを設定
        node_name, base_leaf = find_node_with_cost_standard_flag(nodes_outbound, 100)

        self.base_leaf_name = node_name

        if node_name == None:
            print("NO cost_stantdard = 100 in profile")
        else:
            print(f"Node name: {node_name}, Base leaf: {base_leaf}")



        root_price = set_price_leaf2root(base_leaf, self.root_node_outbound, 100)
        print("root_price", root_price)
        set_value_chain_outbound(root_price, self.root_node_outbound)
        





        # 3. Tree構造の読み込み

        load_directory = self.load_directory

        with open(f"{load_directory}/root_node_outbound.pkl", 'rb') as f:
            self.root_node_outbound = pickle.load(f)
            print(f"root_node_outbound loaded: {self.root_node_outbound}")

        with open(f"{load_directory}/root_node_inbound.pkl", 'rb') as f:
            self.root_node_inbound = pickle.load(f)
            print(f"root_node_inbound loaded: {self.root_node_inbound}")



        ## 4. PSIPlannerAppのデータ・インスタンスの読み込み
        #with open(f"{load_directory}/psi_planner_app.pkl", 'rb') as f:
        #    loaded_attributes = pickle.load(f)
        #    self.__dict__.update(loaded_attributes)
        #    print(f"loaded_attributes: {loaded_attributes}")



        # 選択的に項目を更新してNetworkX Graphを再描画

        ## 特定の項目を選択的に更新
        #self.decouple_node_selected = psi_planner_app_work.decouple_node_selected
        self.selective_update(load_directory)




        # 5. nodes_outboundとnodes_inboundを再生成
        self.nodes_outbound = self.regenerate_nodes(self.root_node_outbound)
        self.nodes_inbound = self.regenerate_nodes(self.root_node_inbound)


        # network area
        print("load_from_directory self.decouple_node_selected", self.decouple_node_selected)


        decouple_node_names = self.decouple_node_selected







        # グラフ`G`と位置情報`pos_E2E`を確認 
        print("Graph G:", self.G)
        print("Position pos_E2E:", self.pos_E2E)


        #nx.draw(self.G, self.pos_E2E)

        #self.draw_network4opt( self.G, self.Gdm_structure, self.Gsp, self.pos_E2E, self.flowDict_opt)
        #self.draw_network(self.G, self.Gdm_structure, self.Gsp, self.pos_E2E)





        #@241221 STOP for LOADSAVE RUN

        ##@241209 ADD decouple_node clearing STOP 4LOADSAVE
        #self.decouple_node_selected = []

        #@241221 TEST STOP RUN
        self.view_nx_matlib()

        
        
        self.root.after(1000, self.show_psi_graph)
        
        # パラメータの初期化と更新を呼び出し
        self.initialize_parameters()







#    def save_data(self, save_directory):
#        psi_planner_app_save = PSIPlannerApp4save()
#        psi_planner_app_save.update_from_psiplannerapp(self)
#        with open(os.path.join(save_directory, 'psi_planner_app.pkl'), "wb") as f:
#            pickle.dump(psi_planner_app_save.__dict__, f)
#        print("データを保存しました。")




    def save_data(self, save_directory):

        print(f"保存前 - market_potential: {self.market_potential}, target_share: {self.target_share}")  # ログ追加

        print(f"保存前 - total_revenue : {self.total_revenue}, total_profit : {self.total_profit}")  

        psi_planner_app_save = PSIPlannerApp4save()
        psi_planner_app_save.update_from_psiplannerapp(self)

        print(f"保存時 - market_potential: {psi_planner_app_save.market_potential}, target_share: {psi_planner_app_save.target_share}")  # ログ追加

        print(f"保存時 - total_revenue: {psi_planner_app_save.total_revenue}, total_profit: {psi_planner_app_save.total_profit}")  




        with open(os.path.join(save_directory, 'psi_planner_app.pkl'), "wb") as f:
            pickle.dump(psi_planner_app_save.__dict__, f)
        print("データを保存しました。")








    def save_to_directory(self):
        # 1. Save先となるdirectoryの問い合わせ
        save_directory = filedialog.askdirectory()

        if not save_directory:
            return  # ユーザーがキャンセルした場合

        # 2. 初期処理のcsv fileのコピー
        for filename in os.listdir(self.directory):
            if filename.endswith('.csv'):
                full_file_name = os.path.join(self.directory, filename)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, save_directory)


        # 3. Tree構造の保存
        with open(os.path.join(save_directory, 'root_node_outbound.pkl'), 'wb') as f:
            pickle.dump(self.root_node_outbound, f)
            print(f"root_node_outbound saved: {self.root_node_outbound}")

        with open(os.path.join(save_directory, 'root_node_inbound.pkl'), 'wb') as f:
            pickle.dump(self.root_node_inbound, f)
            print(f"root_node_inbound saved: {self.root_node_inbound}")

        with open(os.path.join(save_directory, 'root_node_out_opt.pkl'), 'wb') as f:
            pickle.dump(self.root_node_out_opt, f)
            print(f"root_node_out_opt saved: {self.root_node_out_opt}")


        # 4. グラフデータの保存
        nx.write_gml(self.G, f"{save_directory}/G.gml")
        nx.write_gml(self.Gdm_structure, f"{save_directory}/Gdm_structure.gml")
        nx.write_gml(self.Gsp, f"{save_directory}/Gsp.gml")
        print(f"グラフが{save_directory}に保存されました")

        nx.write_gpickle(self.G, os.path.join(save_directory, 'G.gpickle'))
        nx.write_gpickle(self.Gdm_structure, os.path.join(save_directory, 'Gdm_structure.gpickle'))
        nx.write_gpickle(self.Gsp, os.path.join(save_directory, 'Gsp.gpickle'))
        print("Graph data saved.")



        # saveの前にself.market_potential,,,をupdate

        #self.initialize_parameters()
        self.updated_parameters()

        # 5. PSIPlannerAppのデータ・インスタンスの保存
        self.save_data(save_directory)

        # 追加：ファイルの存在とサイズの確認
        for filename in ['root_node_outbound.pkl', 'root_node_inbound.pkl', 'psi_planner_app.pkl']:
            full_file_name = os.path.join(save_directory, filename)
            if os.path.exists(full_file_name):
                file_size = os.path.getsize(full_file_name)
                print(f"{filename} exists, size: {file_size} bytes")
            else:
                print(f"{filename} does not exist")

        # 6. 完了メッセージの表示
        messagebox.showinfo("Save Completed", "Plan data save is completed")






    def save_to_directory_OLD(self):

        # 1. Save先となるdirectoryの問い合わせ
        save_directory = filedialog.askdirectory()
        if not save_directory:
            return  # ユーザーがキャンセルした場合

        # 2. 初期処理のcsv fileのコピー
        for filename in os.listdir(self.directory):
            if filename.endswith('.csv'):
                full_file_name = os.path.join(self.directory, filename)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, save_directory)

        # 3. Tree構造の保存
        with open(os.path.join(save_directory, 'root_node_outbound.pkl'), 'wb') as f:
            pickle.dump(self.root_node_outbound, f)
            print(f"root_node_outbound saved: {self.root_node_outbound}")

        with open(os.path.join(save_directory, 'root_node_inbound.pkl'), 'wb') as f:
            pickle.dump(self.root_node_inbound, f)
            print(f"root_node_inbound saved: {self.root_node_inbound}")

        # 4. グラフデータの保存

        ## GML形式でグラフを保存
        #nx.write_gml(self.G, os.path.join(save_directory, "G.gml"))
        #nx.write_gml(self.Gdm_structure, os.path.join(save_directory, "Gdm_structure.gml"))
        #nx.write_gml(self.Gsp, os.path.join(save_directory, "Gsp.gml"))
        #print("グラフがgml形式で保存されました")


        nx.write_gml(self.G, f"{save_directory}/G.gml")
        nx.write_gml(self.Gdm_structure, f"{save_directory}/Gdm_structure.gml")
        nx.write_gml(self.Gsp, f"{save_directory}/Gsp.gml")
        print(f"グラフが{save_directory}に保存されました")





        nx.write_gpickle(self.G, os.path.join(save_directory, 'G.gpickle'))
        nx.write_gpickle(self.Gdm_structure, os.path.join(save_directory, 'Gdm_structure.gpickle'))
        nx.write_gpickle(self.Gsp, os.path.join(save_directory, 'Gsp.gpickle'))

        print("Graph data saved.")

        # 5. PSIPlannerAppのデータ・インスタンスの保存
        def is_picklable(value):
            try:
                pickle.dumps(value)
            except (pickle.PicklingError, TypeError):
                return False
            return True

        attributes_to_save = {key: value for key, value in self.__dict__.items()
                              if is_picklable(value) and not isinstance(value, (tk.Tk, tk.Widget, tk.Toplevel, tk.Variable))}
        with open(os.path.join(save_directory, 'psi_planner_app.pkl'), 'wb') as f:
            pickle.dump(attributes_to_save, f)
            print(f"attributes_to_save: {attributes_to_save}")

        # 追加：ファイルの存在とサイズの確認
        for filename in ['root_node_outbound.pkl', 'root_node_inbound.pkl', 'psi_planner_app.pkl']:
            full_file_name = os.path.join(save_directory, filename)
            if os.path.exists(full_file_name):
                file_size = os.path.getsize(full_file_name)
                print(f"{filename} exists, size: {file_size} bytes")
            else:
                print(f"{filename} does not exist")

        # 5. 完了メッセージの表示
        messagebox.showinfo("Save Completed", "Plan data save is completed")




    def load_from_directory_test(self):
        # 1. Load元となるdirectoryの問い合わせ
        load_directory = filedialog.askdirectory()

        if not load_directory:
            return  # ユーザーがキャンセルした場合

        # 3. Tree構造の読み込み
        with open(f"{load_directory}/root_node_outbound.pkl", 'rb') as f:
            self.root_node_outbound = pickle.load(f)
            print(f"root_node_out_load loaded: {self.root_node_outbound}")

        with open(f"{load_directory}/root_node_inbound.pkl", 'rb') as f:
            self.root_node_inbound = pickle.load(f)
            print(f"root_node_inbound loaded: {self.root_node_inbound}")

        # 4. PSIPlannerAppのデータ・インスタンスの読み込み
        with open(f"{load_directory}/psi_planner_app.pkl", 'rb') as f:
            loaded_attributes = pickle.load(f)
            self.__dict__.update(loaded_attributes)
            print(f"loaded_attributes: {loaded_attributes}")

        # 5. nodes_outboundとnodes_inboundを再生成
        self.nodes_outbound = self.regenerate_nodes(self.root_node_outbound)
        self.nodes_inbound = self.regenerate_nodes(self.root_node_inbound)

        # ネットワークグラフの読み込み
        self.G = nx.read_gml(f"{load_directory}/G.gml")
        self.Gdm_structure = nx.read_gml(f"{load_directory}/Gdm_structure.gml")
        self.Gsp = nx.read_gml(f"{load_directory}/Gsp.gml")



        ## pos_E2Eの適用
        #pos_E2E = self.pos_E2E


        ## pos_E2Eの再計算（必要に応じて）
        #self.pos_E2E = self.calculate_pos_E2E()

        pos_E2E = make_E2E_positions(self.root_node_outbound, self.root_node_inbound)
        pos_E2E = tune_hammock(pos_E2E, self.nodes_outbound, self.nodes_inbound)
        self.pos_E2E = pos_E2E


        # ネットワークグラフの再描画
        self.draw_network4load_test(self.G, self.Gdm_structure, self.Gsp, self.pos_E2E)

        # キャンバスの再描画
        self.canvas_network.draw()

        # 6. 完了メッセージの表示
        messagebox.showinfo("Load Completed", "Plan data load is completed")




    def calculate_pos_E2E(self):
        # pos_E2Eの計算ロジックを定義
        pass

    def draw_network4load_test(self, G, Gdm, Gsp, pos_E2E):
        self.ax_network.clear()

        # 評価結果の更新
        ttl_revenue = self.total_revenue
        ttl_profit = self.total_profit
        ttl_profit_ratio = (ttl_profit / ttl_revenue) if ttl_revenue != 0 else 0

        # 四捨五入して表示
        total_revenue = round(ttl_revenue)
        total_profit = round(ttl_profit)
        profit_ratio = round(ttl_profit_ratio * 100, 1)  # パーセント表示

        self.ax_network.set_title("PySI\nOptimized Supply Chain Network\nRevenue: {} Profit: {}".format(total_revenue, total_profit))
        self.ax_network.axis('off')

        # ノードの描画
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]

        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):
            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax_network)

        # エッジの描画
        for edge in G.edges():
            if edge[0] == "procurement_office" or edge[1] == "sales_office":
                edge_color = 'lightgrey'
            elif edge in Gdm.edges():
                edge_color = 'blue'
            elif edge in Gsp.edges():
                edge_color = 'green'
            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax_network, width=0.5)

        # ラベルの描画
        node_labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax_network)

        self.canvas_network.draw()





    def load_from_directory_test_STOP_GPT(self):
        # 1. Load元となるdirectoryの問い合わせ
        load_directory = filedialog.askdirectory()

        if not load_directory:
            return  # ユーザーがキャンセルした場合

        # 2. Tree構造の読み込み
        with open(f"{load_directory}/root_node_outbound.pkl", 'rb') as f:
            self.root_node_outbound = pickle.load(f)
            print(f"root_node_outbound loaded: {self.root_node_outbound}")

        with open(f"{load_directory}/root_node_inbound.pkl", 'rb') as f:
            self.root_node_inbound = pickle.load(f)
            print(f"root_node_inbound loaded: {self.root_node_inbound}")

        # 3. PSIPlannerAppのデータ・インスタンスの読み込み
        self.load_data(load_directory)

        # 4. nodes_outboundとnodes_inboundを再生成
        self.nodes_outbound = self.regenerate_nodes(self.root_node_outbound)
        self.nodes_inbound = self.regenerate_nodes(self.root_node_inbound)



        #@ STOP
        ## 5. ネットワークグラフの読み込み
        #self.G = nx.read_gml(f"{load_directory}/G.gml")
        #self.Gdm_structure = nx.read_gml(f"{load_directory}/Gdm_structure.gml")


        ## 5. ネットワークグラフの描画
        #self.draw_networkx_graph()

        #@ STOP RUN
        # 5. ネットワークグラフの描画
        self.view_nx_matlib()

        #@ STOP RUN
        # 6. PSIの表示
        self.root.after(1000, self.show_psi("outbound", "supply"))


        # パラメータの初期化と更新を呼び出し
        self.initialize_parameters()


        # 7. 完了メッセージの表示
        messagebox.showinfo("Load Completed", "Plan data load is completed")








    def load_from_directory(self):
        # 1. Load元となるdirectoryの問い合わせ
        load_directory = filedialog.askdirectory()

        if not load_directory:
            return  # ユーザーがキャンセルした場合

        # 2. Tree構造の読み込み
        self.load_directory = load_directory
        self.directory      = load_directory # for "optimized network"
        self._load_tree_structure(load_directory)








        # 3. PSIPlannerAppのデータ・インスタンスの読み込み
        self.load_data(load_directory)

        # if "save files" are NOT optimized one
        if os.path.exists(f"{load_directory}/root_node_out_opt.pkl"):
            pass
        else:
            self.flowDict_opt = {}  # NO optimize



        ## 3. PSIPlannerAppのデータ・インスタンスの読み込みと更新
        #self.selective_update(load_directory)


        # 4. nodes_outboundとnodes_inboundを再生成
        self.nodes_outbound = self.regenerate_nodes(self.root_node_outbound)
        self.nodes_inbound = self.regenerate_nodes(self.root_node_inbound)

        #self.nodes_out_opt = self.regenerate_nodes(self.root_node_out_opt)


        print("load_from_directory self.decouple_node_selected", self.decouple_node_selected)





        #@241224 ADD
        # eval area
        self.update_evaluation_results()


        ## 5. ネットワークグラフの描画
        #self.draw_networkx_graph()

        #@ STOP RUN change2OPT
        # 5. ネットワークグラフの描画

        self.view_nx_matlib4opt()

        #self.view_nx_matlib()


        #@ MOVED
        self.updated_parameters()


        #@ STOP RUN
        # 6. PSIの表示
        if self.root_node_out_opt == None:
            self.root.after(1000, self.show_psi("outbound", "supply"))

            #@ STOP
            ## パラメータの初期化と更新を呼び出し
            #self.updated_parameters()

        else:  # is root_node_out_opt
            self.root.after(1000, self.show_psi_graph4opt)


            #@ STOP
            ## パラメータの初期化と更新を呼び出し
            #self.set_market_potential(self.root_node_out_opt)
            #self.updated_parameters()
            ##self.initialize_parameters()





        # 7. 完了メッセージの表示
        messagebox.showinfo("Load Completed", "Plan data load is completed")







    def set_market_potential(self, root):

        # **************************************
        # count_lots_on_S_psi4demand
        # **************************************
        # psi4demand[w][0]の配置されたSのlots数を年別にcountしてlist化

        plan_year_st = self.plan_year_st
        plan_range   = self.plan_range



        def count_lots_on_S_psi4demand(node, S_list):
            if node.children == []:
                for w_psi in node.psi4demand:
                    S_list.append(w_psi[0])
            for child in node.children:
                count_lots_on_S_psi4demand(child, S_list)
            return S_list

        S_list = []

        year_lots_list4S = []

        S_list = count_lots_on_S_psi4demand(root, S_list)
        #S_list = count_lots_on_S_psi4demand(root_node_outbound, S_list)

        
        for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):
            year_lots4S = count_lots_yyyy(S_list, str(yyyy))
            year_lots_list4S.append(year_lots4S)
        
        # 値をインスタンス変数に保存
        self.market_potential = year_lots_list4S[1]  

        print("self.market_potential", self.market_potential)


        #@ STOP
        #self.total_supply_plan = round(self.global_market_potential * self.target_share)
        #
        ##self.total_supply_plan = self.global_market_potential
        #print("self.total_supply_plan", self.total_supply_plan)















    def _load_tree_structure(self, load_directory):

        with open(f"{load_directory}/root_node_outbound.pkl", 'rb') as f:
            self.root_node_outbound = pickle.load(f)
            print(f"root_node_outbound loaded: {self.root_node_outbound}")

        with open(f"{load_directory}/root_node_inbound.pkl", 'rb') as f:
            self.root_node_inbound = pickle.load(f)
            print(f"root_node_inbound loaded: {self.root_node_inbound}")


        if os.path.exists(f"{load_directory}/root_node_out_opt.pkl"):
            with open(f"{load_directory}/root_node_out_opt.pkl", 'rb') as f:
                self.root_node_out_opt = pickle.load(f)
                print(f"root_node_out_opt loaded: {self.root_node_out_opt}")
        else:
            self.flowDict_opt = {}  # NO optimize
            pass



    def selective_update(self, load_directory):
        # 一時データを別インスタンスにロード
        psi_planner_app_work = PSIPlannerApp(self.root)  # rootを渡してインスタンスを作成
        print("PSIPlannerApp(self.root) is instanciated")

        with open(f"{load_directory}/psi_planner_app.pkl", 'rb') as f:
            loaded_attributes = pickle.load(f)
            psi_planner_app_work.__dict__.update(loaded_attributes)
            print(f"Loaded attributes for temporary instance: {loaded_attributes}")

        # 特定の項目を選択的に更新
        self.decouple_node_selected = psi_planner_app_work.decouple_node_selected
        self.G                      = psi_planner_app_work.G
        self.Gdm                    = psi_planner_app_work.Gdm
        self.Gdm_structure          = psi_planner_app_work.Gdm_structure
        self.Gsp                    = psi_planner_app_work.Gsp
        self.pos_E2E                = psi_planner_app_work.pos_E2E

        self.total_revenue          = psi_planner_app_work.total_revenue
        self.total_profit           = psi_planner_app_work.total_profit

        self.flowDict_opt           = psi_planner_app_work.flowDict_opt
        self.flowCost_opt           = psi_planner_app_work.flowCost_opt
                          
        self.market_potential       = psi_planner_app_work.market_potential
        self.target_share           = psi_planner_app_work.target_share    




    def draw_networkx_graph(self):

        self.ax_network.clear()  # 以前の描画をクリア

        nx.draw(self.G, pos=self.pos_E2E, ax=self.ax_network, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_color="black", font_weight="bold", edge_color="gray")
        self.canvas_network.draw()





    def regenerate_nodes(self, root_node):
        nodes = {}

        def traverse(node):
            nodes[node.name] = node
            for child in node.children:
                traverse(child)

        traverse(root_node)
        return nodes








    def save_data_files(self):
        # セーブ機能の実装
        print("TO BE implemented...")
        pass



        def count_lots_on_S_psi4demand(node, S_list):

            # leaf_node末端市場の判定
            if node.children == []:  # 子nodeがないleaf nodeの場合

                # psi_listからS_listを生成する
                for w_psi in node.psi4demand:  # weeklyのSをS_listに集計

                    S_list.append(w_psi[0])

            else:
                pass

            for child in node.children:
                count_lots_on_S_psi4demand(child, S_list)

            return S_list


        S_list = []
        year_lots_list4S = []

        # treeを生成した直後なので、root_node_outboundが使える
        S_list = count_lots_on_S_psi4demand(root_node_outbound, S_list)

            # 開始年を取得する
        plan_year_st = year_st  # 開始年のセット in main()要修正
        
        for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):
        
            year_lots4S = count_lots_yyyy(S_list, str(yyyy))
        
            year_lots_list4S.append(year_lots4S)
        
            #        # 結果を出力
            #       #print(yyyy, " year carrying lots:", year_lots)
            #
            #    # 結果を出力
            #   #print(" year_lots_list:", year_lots_list)
        
            # an image of sample data
            #
            # 2023  year carrying lots: 0
            # 2024  year carrying lots: 2919
            # 2025  year carrying lots: 2914
            # 2026  year carrying lots: 2986
            # 2027  year carrying lots: 2942
            # 2028  year carrying lots: 2913
            # 2029  year carrying lots: 0
            #
            # year_lots_list4S: [0, 2919, 2914, 2986, 2942, 2913, 0]

            #@241124 CHECK

        #@241205 STOP 
        #print("year_lots_list4S", year_lots_list4S)

        #self.global_market_potential = year_lots_list4S[1]

        #print("self.global_market_potential", self.global_market_potential)



        for filename in os.listdir(directory):

            if filename.endswith(".csv"):

                filepath = os.path.join(directory, filename)

                print(f"Loading file: {filename}")


                if "outbound" in filename.lower():
                    self.outbound_data.append(pd.read_csv(filepath))
                elif "inbound" in filename.lower():
                    self.inbound_data.append(pd.read_csv(filepath))
        print("Outbound files loaded.")
        print("Inbound files loaded.")





        # ***********************************
        # setting price and costs on supply chain tree node
        # ***********************************

        # 足元の大きな主要市場の価格を100として、価格連鎖を計算
        # base_leaf_node be set 100 as final market price

        base_leaf = self.nodes_outbound[self.base_leaf_name]

        # root_price is the shipped lot price linking with the "leaf price"
        # backward setting leaf2root
        root_price = set_price_leaf2root(base_leaf, self.root_node_outbound, 100)
        print("root_price", root_price)

        set_value_chain_outbound(root_price, self.root_node_outbound) # 




        # ***********************************
        # viewer
        # ***********************************
        self.view_nx_matlib()

        self.root.after(1000, self.show_psi_graph)








    def load_data_files4opt(self):

    #@RENAME
    # nodes_outbound     : nodes_out_opt    
    # root_node_outbound : root_node_out_opt


        # setting directory from "plan"
        directory = self.directory


        #@ STOP
        #directory = filedialog.askdirectory(title="Select Data Directory")


        if directory:

            # ***********************
            # Lot sizeを取得して変換
            # ***********************
            #try:
            #    self.lot_size = int(self.lot_size_entry.get())
            #except ValueError:
            #    print("Invalid lot size input. Using default value.")

            # Lot size, Plan Year Start, and Plan Rangeを取得して変換
            try:
                self.lot_size = int(self.lot_size_entry.get())
                self.plan_year_st = int(self.plan_year_entry.get())
                self.plan_range = int(self.plan_range_entry.get())
            except ValueError:
                print("Invalid input for lot size, plan year start, or plan range. Using default values.")

            self.outbound_data = []
            self.inbound_data = []

            print("os.listdir(directory)",os.listdir(directory))

            data_file_list = os.listdir(directory)


            # save directory
            self.directory = directory


            # ************************
            # read "profile_tree_outbound.csv"
            # build tree_outbound
            # ************************
            if "profile_tree_outbound.csv" in data_file_list:

                filename = "profile_tree_outbound.csv"

                file_path = os.path.join(directory, filename)
                #filepath = os.path.join(directory, filename)


                #load_outbound(outbound_tree_file)


                # ***************************
                # set file name for "profile tree"
                # ***************************
                #outbound_tree_file = "profile_tree_outbound.csv"
                #inbound_tree_file = "profile_tree_inbound.csv"

                # ***************************
                # create supply chain tree for "out"bound + optimization
                # ***************************

                # because of the python interpreter performance point of view,
                # this "create tree" code be placed in here, main process

            #@240830
            # "nodes_xxxx" is dictionary to get "node pointer" from "node name"
                nodes_out_opt = {}
                nodes_out_opt, root_node_name_out = create_tree_set_attribute(file_path)

                print("root_node_name_out",root_node_name_out)

                root_node_out_opt = nodes_out_opt[root_node_name_out]




                def make_leaf_nodes(node, list):
                    if node.children == []: # leaf_nodeの場合
                        list.append(node.name)
                    else:
                        pass

                    for child in node.children:
                        make_leaf_nodes(child, list)

                    return list

                leaf_nodes_opt = []
                leaf_nodes_opt = make_leaf_nodes(root_node_out_opt, leaf_nodes_opt)



                # making balance for nodes



                # ********************************
                # set outbound tree handle
                # ********************************
                self.nodes_out_opt = nodes_out_opt
                self.root_node_out_opt = root_node_out_opt


                print("leaf_nodes_opt", leaf_nodes_opt)
                self.leaf_nodes_opt = leaf_nodes_opt

                # ********************************
                # tree wideth/depth count and adjust
                # ********************************
                set_positions(root_node_out_opt)



                # root_node_out_opt = nodes_out_opt['JPN']      # for test, direct define
                # root_node_out_opt = nodes_out_opt['JPN_OUT']  # for test, direct define

                # setting parent on its child
                set_parent_all(root_node_out_opt)
                print_parent_all(root_node_out_opt)

            else:
                print("error: profile_tree_outbound.csv is missed")
                pass


            # ************************
            # read "profile_tree_inbound.csv"
            # build tree_inbound
            # ************************
            if "profile_tree_inbound.csv" in data_file_list:

                filename = "profile_tree_inbound.csv"
                file_path = os.path.join(directory, filename)


                # ***************************
                # create supply chain tree for "in"bound
                # ***************************
                nodes_inbound = {}

                nodes_inbound, root_node_name_in = create_tree_set_attribute(file_path)
                root_node_inbound = nodes_inbound[root_node_name_in]


                # ********************************
                # set inbound tree handle
                # ********************************
                self.nodes_inbound = nodes_inbound
                self.root_node_inbound = root_node_inbound


                # ********************************
                # tree wideth/depth count and adjust
                # ********************************
                set_positions(root_node_inbound)

                # setting parent on its child
                set_parent_all(root_node_inbound)
                print_parent_all(root_node_inbound)

            else:
                print("error: profile_tree_inbound.csv is missed")

                pass




            # ************************
            # read "node_cost_table_outbound.csv"
            # read_set_cost
            # ************************
            if "node_cost_table_outbound.csv" in data_file_list:

                filename = "node_cost_table_outbound.csv"
                file_path = os.path.join(directory, filename)

                read_set_cost(file_path, nodes_out_opt)

            else:
                print("error: node_cost_table_outbound.csv is missed")

                pass




            # ************************
            # read "node_cost_table_inbound.csv"
            # read_set_cost
            # ************************
            if "node_cost_table_inbound.csv" in data_file_list:

                filename = "node_cost_table_inbound.csv"
                file_path = os.path.join(directory, filename)

                read_set_cost(file_path, nodes_inbound)


            else:
                print("error: node_cost_table_inbound.csv is missed")

                pass









            # ***************************
            # make price chain table
            # ***************************

            # すべてのパスを見つける
            paths = find_paths(root_node_out_opt)

            # 各リストをタプルに変換してsetに変換し、重複を排除
            unique_paths = list(set(tuple(x) for x in paths))

            # タプルをリストに戻す
            unique_paths = [list(x) for x in unique_paths]

            print("")
            print("")

            for path in unique_paths:
                print(path)

            sorted_paths = sorted(paths, key=len)

            print("")
            print("")

            for path in sorted_paths:
                print(path)


            #@241224 MARK4OPT_SAVE
            # ************************
            # read "S_month_optimized.csv"
            # trans_month2week2lot_id_list
            # ************************
            if "S_month_optimized.csv" in data_file_list:
            #if "S_month_data.csv" in data_file_list:

                filename = "S_month_optimized.csv"
                in_file_path = os.path.join(directory, filename)


                print("self.lot_size",self.lot_size)

                # 使用例
                #in_file = "S_month_data.csv"
                df_weekly, plan_range, plan_year_st = trans_month2week2lot_id_list(in_file_path, self.lot_size)

                print("plan_year_st",plan_year_st)
                print("plan_range",plan_range)

                # update plan_year_st plan_range
                self.plan_year_st = plan_year_st  # S_monthで更新
                self.plan_range   = plan_range    # S_monthで更新


                # Update the GUI fields
                self.plan_year_entry.delete(0, tk.END)
                self.plan_year_entry.insert(0, str(self.plan_year_st))
                self.plan_range_entry.delete(0, tk.END)
                self.plan_range_entry.insert(0, str(self.plan_range))


                out_file = "S_iso_week_data_opt.csv"
                out_file_path = os.path.join(directory, out_file)

                df_weekly.to_csv(out_file_path, index=False)

                df_capa_year = make_capa_year_month(in_file_path)

                #@241112 test
                year_st = df_capa_year["year"].min()
                year_end = df_capa_year["year"].max()
                print("year_st, year_end",year_st, year_end)

            else:
                print("error: S_month_optimized.csv is missed")

                pass


            #@241124 ココは、初期のEVAL処理用パラメータ。現在は使用していない
            # planning parameterをNode method(=self.)でセットする。
            # plan_range, lot_counts, cash_in, cash_out用のparameterをセット

            root_node_out_opt.set_plan_range_lot_counts(plan_range, plan_year_st)
            root_node_inbound.set_plan_range_lot_counts(plan_range, plan_year_st)

            # ***************************
            # an image of data
            #
            # for node_val in node_yyyyww_value:
            #   #print( node_val )
            #
            ##['SHA_N', 22.580645161290324, 22.580645161290324, 22.580645161290324, 22.5    80645161290324, 26.22914349276974, 28.96551724137931, 28.96551724137931, 28.    96551724137931, 31.067853170189103, 33.87096774193549, 33.87096774193549, 33    .87096774193549, 33.87096774193549, 30.33333333333333, 30.33333333333333, 30    .33333333333333, 30.33333333333333, 31.247311827956988, 31.612903225806452,

            # node_yyyyww_key [['CAN', 'CAN202401', 'CAN202402', 'CAN202403', 'CAN20240    4', 'CAN202405', 'CAN202406', 'CAN202407', 'CAN202408', 'CAN202409', 'CAN202    410', 'CAN202411', 'CAN202412', 'CAN202413', 'CAN202414', 'CAN202415', 'CAN2    02416', 'CAN202417', 'CAN202418', 'CAN202419',

            # ********************************
            # make_node_psi_dict
            # ********************************
            # 1. treeを生成して、nodes[node_name]辞書で、各nodeのinstanceを操作        する
            # 2. 週次S yyyywwの値valueを月次Sから変換、
            #    週次のlotの数Slotとlot_keyを生成、
            # 3. ロット単位=lot_idとするリストSlot_id_listを生成しながらpsi_list        生成
            # 4. node_psi_dict=[node1: psi_list1,,,]を生成、treeのnode.psi4deman        dに接続する
        
            S_week = []
        
            # *************************************************
            # node_psi辞書を初期セットする
            # initialise node_psi_dict
            # *************************************************
            node_psi_dict = {}  # 変数 node_psi辞書
        
            # ***************************
            # outbound psi_dic
            # ***************************
            node_psi_dict_Ot4Dm = {}  # node_psi辞書Outbound4Demand plan
            node_psi_dict_Ot4Sp = {}  # node_psi辞書Outbound4Supply plan
        
            # coupling psi
            node_psi_dict_Ot4Cl = {}  # node_psi辞書Outbound4Couple plan

            # accume psi
            node_psi_dict_Ot4Ac = {}  # node_psi辞書Outbound4Accume plan
        
            # ***************************
            # inbound psi_dic
            # ***************************
            node_psi_dict_In4Dm = {}  # node_psi辞書Inbound4demand plan
            node_psi_dict_In4Sp = {}  # node_psi辞書Inbound4supply plan
        
            # coupling psi
            node_psi_dict_In4Cl = {}  # node_psi辞書Inbound4couple plan
        
            # accume psi
            node_psi_dict_In4Ac = {}  # node_psi辞書Inbound4accume plan

            # ***************************
            # rootからtree nodeをpreorder順に検索 node_psi辞書に空リストをセット        する
            # psi_list = [[[] for j in range(4)] for w in range(53 * plan_range)        ]
            # ***************************
            node_psi_dict_Ot4Dm = make_psi_space_dict(
        root_node_out_opt, node_psi_dict_Ot4Dm, plan_range
            )
            node_psi_dict_Ot4Sp = make_psi_space_dict(
                root_node_out_opt, node_psi_dict_Ot4Sp, plan_range
            )
            node_psi_dict_Ot4Cl = make_psi_space_dict(
                root_node_out_opt, node_psi_dict_Ot4Cl, plan_range
            )
            node_psi_dict_Ot4Ac = make_psi_space_dict(
                root_node_out_opt, node_psi_dict_Ot4Ac, plan_range
            )
        
            node_psi_dict_In4Dm = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Dm, plan_range
            )
            node_psi_dict_In4Sp = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Sp, plan_range
            )
            node_psi_dict_In4Cl = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Cl, plan_range
            )
            node_psi_dict_In4Ac = make_psi_space_dict(
                root_node_inbound, node_psi_dict_In4Ac, plan_range
            )
        
            # ***********************************
            # set_dict2tree
            # ***********************************
            # rootからtreeをpreorder順に検索
            # node_psi辞書内のpsi_list pointerをNodeのnode objectにsetattr()で接        続
        
            set_dict2tree_psi(root_node_out_opt, "psi4demand", node_psi_dict_Ot4Dm)
            set_dict2tree_psi(root_node_out_opt, "psi4supply", node_psi_dict_Ot4Sp)
            set_dict2tree_psi(root_node_out_opt, "psi4couple", node_psi_dict_Ot4Cl)
            set_dict2tree_psi(root_node_out_opt, "psi4accume", node_psi_dict_Ot4Ac)
        
            set_dict2tree_psi(root_node_inbound, "psi4demand", node_psi_dict_In4Dm)
            set_dict2tree_psi(root_node_inbound, "psi4supply", node_psi_dict_In4Sp)
            set_dict2tree_psi(root_node_inbound, "psi4couple", node_psi_dict_In4Cl)
            set_dict2tree_psi(root_node_inbound, "psi4accume", node_psi_dict_In4Ac)
        








            #@241224 MARK4OPT_SAVE
            #
            # ココで、root_node_out_optのPSIがsetされ、planning engineに渡る
            #
            # ************************************
            # setting S on PSI
            # ************************************

            # Weekly Lot: CPU:Common Planning UnitをPSI spaceにセットする
            set_df_Slots2psi4demand(root_node_out_opt, df_weekly)



            #@241124 adding for "global market potential"
            # ************************************
            # counting all lots
            # ************************************

            #print("check lots on psi4demand[w][0] ")

            ## count lot on all nodes  from  node.psi4demand[w][0] 
            #lot_num = count_lot_all_nodes(root_node_out_opt)

            # year_st
            # year_end

            # **************************************
            # count_lots_on_S_psi4demand
            # **************************************
            # psi4demand[w][0]の配置されたSのlots数を年別にcountしてlist化


            def count_lots_on_S_psi4demand(node, S_list):
                if node.children == []:
                    for w_psi in node.psi4demand:
                        S_list.append(w_psi[0])
                for child in node.children:
                    count_lots_on_S_psi4demand(child, S_list)
                return S_list

            S_list = []
            year_lots_list4S = []
            S_list = count_lots_on_S_psi4demand(root_node_out_opt, S_list)
            plan_year_st = year_st
            
            for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):
                year_lots4S = count_lots_yyyy(S_list, str(yyyy))
                year_lots_list4S.append(year_lots4S)
            
            #@241205 STOP NOT change "global_market_potential" at 2nd loading
            ## 値をインスタンス変数に保存
            #self.global_market_potential = year_lots_list4S[1]  


            print("NOT change #market_potential# at 2nd loading")
            print("self.market_potential", self.market_potential)




        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                filepath = os.path.join(directory, filename)
                print(f"Loading file: {filename}")
                if "outbound" in filename.lower():
                    self.outbound_data.append(pd.read_csv(filepath))
                elif "inbound" in filename.lower():
                    self.inbound_data.append(pd.read_csv(filepath))
        print("Outbound files loaded.")
        print("Inbound files loaded.")



        #@ STOP optimize processでは初期loadのcost_stracture設定で完了している
        #base_leaf = self.nodes_outbound[self.base_leaf_name]
        #
        #root_price = set_price_leaf2root(base_leaf,self.root_node_out_opt,100)
        #print("root_price", root_price)
        #set_value_chain_outbound(root_price, self.root_node_out_opt)
        

        self.view_nx_matlib()
        self.root.after(1000, self.show_psi_graph)

        #@241222@ STOP RUN
        # パラメータの初期化と更新を呼び出し
        self.initialize_parameters()


        def count_lots_on_S_psi4demand(node, S_list):

            # leaf_node末端市場の判定
            if node.children == []:  # 子nodeがないleaf nodeの場合

                # psi_listからS_listを生成する
                for w_psi in node.psi4demand:  # weeklyのSをS_listに集計

                    S_list.append(w_psi[0])

            else:
                pass

            for child in node.children:
                count_lots_on_S_psi4demand(child, S_list)

            return S_list


        S_list = []
        year_lots_list4S = []

        # treeを生成した直後なので、root_node_out_optが使える
        S_list = count_lots_on_S_psi4demand(root_node_out_opt, S_list)

            # 開始年を取得する
        plan_year_st = year_st  # 開始年のセット in main()要修正
        
        for yyyy in range(plan_year_st, plan_year_st + plan_range + 1):
        
            year_lots4S = count_lots_yyyy(S_list, str(yyyy))
        
            year_lots_list4S.append(year_lots4S)
        
            #        # 結果を出力
            #       #print(yyyy, " year carrying lots:", year_lots)
            #
            #    # 結果を出力
            #   #print(" year_lots_list:", year_lots_list)
        
            # an image of sample data
            #
            # 2023  year carrying lots: 0
            # 2024  year carrying lots: 2919
            # 2025  year carrying lots: 2914
            # 2026  year carrying lots: 2986
            # 2027  year carrying lots: 2942
            # 2028  year carrying lots: 2913
            # 2029  year carrying lots: 0
            #
            # year_lots_list4S: [0, 2919, 2914, 2986, 2942, 2913, 0]

            #@241124 CHECK

        #@241205 STOP NOT change "market_potential" at 2nd loading
        ## 値をインスタンス変数に保存
        #self.market_potential = year_lots_list4S[1]  

        #print("year_lots_list4S", year_lots_list4S)

        #self.global_market_potential = year_lots_list4S[1]

        #print("self.global_market_potential", self.global_market_potential)



        for filename in os.listdir(directory):

            if filename.endswith(".csv"):

                filepath = os.path.join(directory, filename)

                print(f"Loading file: {filename}")


                if "outbound" in filename.lower():
                    self.outbound_data.append(pd.read_csv(filepath))
                elif "inbound" in filename.lower():
                    self.inbound_data.append(pd.read_csv(filepath))
        print("Outbound files loaded.")
        print("Inbound files loaded.")











# ******************************
# define planning ENGINE
# ******************************

                ## ********************************
                ## set outbound tree handle
                ## ********************************
                #self.nodes_outbound = nodes_outbound
                #self.root_node_outbound = root_node_outbound

                ## ********************************
                ## set inbound tree handle
                ## ********************************
                #self.nodes_inbound = nodes_inbound
                #self.root_node_inbound = root_node_inbound



    def demand_planning(self):
        # Implement forward planning logic here
        print("Forward planning executed.")

        #@240903@241106
        calc_all_psi2i4demand(self.root_node_outbound)


        self.update_evaluation_results()

        #@241212 add
        self.decouple_node_selected = []
        self.view_nx_matlib()

        self.root.after(1000, self.show_psi_graph)
        #self.show_psi_graph() # this event do not live 




    def load_plan_from_directory(self):

        print("optimizing start")

        ##@240903@241106 this is just "demand_plan"
        #calc_all_psi2i4demand(self.root_node_outbound)

        self.update_evaluation_results()

        self.load_plan_and_view_nx_matlib()


        #self.root.after(1000, self.show_psi_graph)
        ##self.show_psi_graph() # this event do not live 







    def optimize_network_NEW(self):
        print("optimizing start")

        self.initialize_graphs()

        pos_E2E = self.show_network_E2E_matplotlib_with_self()
    
        G_opt = self.Gdm_structure.copy()

        self.optimize(G_opt)
    
        optimized_nodes = self.create_optimized_tree(self.flowDict_opt)
        if not optimized_nodes:
            error_message = "error: optimization with NOT enough supply"
            print(error_message)
            self.show_error_message(error_message)
            return
    
        self.process_optimization_results(optimized_nodes)

        self.update_input_csv()

        self.execute_planning_with_optimized_data()

        self.finalize_and_display_results()




    def initialize_graphs(self):
        self.G = nx.DiGraph()
        self.Gdm_structure = nx.DiGraph()
        self.Gsp = nx.DiGraph()


    def show_network_E2E_matplotlib_with_self(self):
        root_node_outbound = self.root_node_outbound
        nodes_outbound = self.nodes_outbound
        root_node_inbound = self.root_node_inbound
        nodes_inbound = self.nodes_inbound
        return self.show_network_E2E_matplotlib(
            root_node_outbound, nodes_outbound, 
            root_node_inbound, nodes_inbound, 
            self.G, self.Gdm_structure, self.Gsp
        )


    def optimize(self, G_opt):
        self.reset_optimization_params(G_opt)
        self.set_optimization_params(G_opt)
        self.run_optimization(G_opt)
        print("run_optimization self.flowDict_opt", self.flowDict_opt)
        self.reset_optimized_path(G_opt)
        self.add_optimized_path(G_opt, self.flowDict_opt)
        print("Optimized Path:", self.flowDict_opt)
        print("Optimized Cost:", self.flowCost_opt)
    
    def process_optimization_results(self, optimized_nodes):
        optimized_root = optimized_nodes['supply_point']
        self.optimized_root = optimized_root

        leaf_nodes_out = self.leaf_nodes_out
        optimized_nodes_list = list(optimized_nodes.keys())
        limited_supply_nodes = [node for node in leaf_nodes_out if node not in optimized_nodes_list]

        print("optimized_nodes_list:", optimized_nodes_list)
        print("limited_supply_nodes:", limited_supply_nodes)
        self.limited_supply_nodes = limited_supply_nodes

    def update_input_csv(self):
        input_csv = 'S_month_data.csv'
        if self.directory is None or input_csv is None:
            raise ValueError("self.directory または input_csv が None になっています。適切な値を設定してください。")

        input_csv_path = os.path.join(self.directory, input_csv)
        output_csv = 'S_month_optimized.csv'
        output_csv_path = os.path.join(self.directory, output_csv)
        self.clear_s_values(self.limited_supply_nodes, input_csv_path, output_csv_path)

    def execute_planning_with_optimized_data(self):
        self.load_data_files4opt()
        self.plan_through_engines4opt()


    def finalize_and_display_results(self):

        self.update_evaluation_results4optimize()
        pos_E2E = self.show_network_E2E_matplotlib()
        self.draw_network4opt(self.G, self.Gdm_structure, self.Gsp, pos_E2E, self.flowDict_opt)

        self.root.after(1000, self.show_psi_graph4opt)
        self.updated_parameters4opt()







    def optimize_network(self):

        print("optimizing start")

        ##@240903@241106 this is just "demand_plan"
        #calc_all_psi2i4demand(self.root_node_outbound)

        #@241220 STOP
        #self.update_evaluation_results4optimize() #with self.root_node_out_opt

        #@241220 STOP
        #self.update_evaluation_results()

        #@ STOP
        #self.optimize_and_view_nx_matlib()


        #self.root.after(1000, self.show_psi_graph)
        ##self.show_psi_graph() # this event do not live 


    #@ STOP
    #def optimize_and_view_nx_matlib(self):

        G = nx.DiGraph()    # base display field


        Gdm_structure = nx.DiGraph()  # optimise for demand side
        #Gdm = nx.DiGraph()  # optimise for demand side

        Gsp = nx.DiGraph()  # optimise for supply side

        self.G = G
        self.Gdm_structure = Gdm_structure
        self.Gsp = Gsp


        root_node_outbound = self.root_node_outbound 
        nodes_outbound = self.nodes_outbound     
        root_node_inbound = self.root_node_inbound  
        nodes_inbound = self.nodes_inbound      

        pos_E2E, G, Gdm_structure, Gsp = self.show_network_E2E_matplotlib(
        #pos_E2E, Gdm_structure, Gsp = show_network_E2E_matplotlib(
        #pos_E2E, flowDict_dm, flowDict_sp, Gdm_structure, Gsp = show_network_E2E_matplotlib(
            root_node_outbound, nodes_outbound, 
            root_node_inbound, nodes_inbound, 
            G, Gdm_structure, Gsp
        )


        # **************************************************
        # optimizing here
        # **************************************************

        G_opt = Gdm_structure.copy()







        # 最適化パラメータをリセット
        self.reset_optimization_params(G_opt)

        #@241229 ADD
        self.reset_optimized_path(G_opt)

        # 新しい最適化パラメータを設定
        self.set_optimization_params(G_opt)

        flowDict_opt = self.flowDict_opt
        print("optimizing here flowDict_opt", flowDict_opt)


        # 最適化を実行
        # fllowing set should be done here
        #self.flowDict_opt = flowDict_opt
        #self.flowCost_opt = flowCost_opt

        self.run_optimization(G_opt)
        print("1st run_optimization self.flowDict_opt", self.flowDict_opt)







        # flowCost_opt = self.flowCost_opt # direct input

        G_result = G_opt.copy()


        G_view = G_result.copy()
        self.add_optimized_path(G_view, self.flowDict_opt)



        # 6. パラメータリセットとシミュレーション繰り返し

#        # 前回の最適化pathをリセット
#        self.reset_optimized_path(G_result)
#        
#        # 新しい最適化pathを追加
#        #G_result = G_opt.copy()
#        self.add_optimized_path(G_result, flowDict_opt)
#    
#        # 最適化pathの表示（オプション）
#        #print("Iteration", i + 1)
#        print("Optimized Path:", flowDict_opt)
#        print("Cost:", flowCost_opt)
#
#
#        G_view = G_result.copy()
#
#        # 修正後のコードでadd_optimized_pathを呼び出します
#        add_optimized_path(G_view, flow_dict)
#
#
#






        #@241227 STOP double definition
        # *********************************
        ## 最適化パラメータをリセット
        #self.reset_optimization_params(G_opt)
        #
        ## 新しい最適化パラメータを設定
        #self.set_optimization_params(G_opt)
        #
        ## 最適化を実行
        ## fllowing set should be done here
        ##self.flowDict_opt = flowDict_opt
        #self.flowCost_opt = flowCost_opt
        #
        #self.run_optimization(G_opt)
        #print("2nd run_optimization self.flowDict_opt", self.flowDict_opt)







        #@241205 STOP **** flowDict_optを使ったGのE2Eの表示系に任せる
        ## 前回の最適化pathをリセット
        self.reset_optimized_path(G_result)
        #
        ## 新しい最適化pathを追加
        G_result = G_opt.copy()
        self.add_optimized_path(G_result, self.flowDict_opt)
        
        # 最適化pathの表示（オプション）
        #print("Iteration", i + 1)
        print("Optimized Path:", self.flowDict_opt)
        print("Optimized Cost:", self.flowCost_opt)


        # make optimized tree and PSI planning and show it
        flowDict_opt = self.flowDict_opt


        optimized_nodes = {} # 初期化
        optimized_nodes = self.create_optimized_tree(flowDict_opt)


        if not optimized_nodes:
            error_message = "error: optimization with NOT enough supply"
            print(error_message)
            self.show_error_message(error_message)  # 画面にエラーメッセージを表示する関数
            return


        print("optimized_nodes", optimized_nodes)
        optimized_root = optimized_nodes['supply_point']
        self.optimized_root = optimized_root



        #@241227 MEMO 
        # 最適化されたnodeの有無でPSI表示をON/OFFしているが、これに加えて
        # ここでは、最適化nodeは存在し、、年間の値が0の時、
        # 年間供給量を月次に按分して供給するなどの処理を追加する



        # *********************************
        # making limited_supply_nodes
        # *********************************
        leaf_nodes_out       = self.leaf_nodes_out  # all leaf_nodes
        optimized_nodes_list = []              # leaf_node on targetted market
        limited_supply_nodes = []              # leaf_node Removed from target

        # 1. optimized_nodes辞書からキー項目をリストoptimized_nodes_listに抽出
        optimized_nodes_list = list(optimized_nodes.keys())

        # 2. leaf_nodes_outからoptimized_nodes_listの要素を排除して
        # limited_supply_nodesを生成
        limited_supply_nodes = [node for node in leaf_nodes_out if node not in optimized_nodes_list]

        # 結果を表示
        print("optimized_nodes_list:", optimized_nodes_list)
        print("limited_supply_nodes:", limited_supply_nodes)


# 最適化の結果をPSIに反映する方法
# 1. 入力ファイルS_month_data.csvをdataframeに読込み
# 2. limited_supply_nodesの各要素node nameに該当するS_month_dataのSの値を
#    すべて0 clearする。
# 3. 結果を"S_month_optimized.csv"として保存する
# 4. S_month_optimized.csvを入力として、load_data_opt_filesからPSI planする



        # limited_supply_nodesのリスト
        #limited_supply_nodes = ['MUC_N', 'MUC_D', 'MUC_I', 'SHA_I', 'NYC_D', 'NYC_I', 'LAX_D', 'LAX_I']












        # 入力CSVファイル名
        input_csv = 'S_month_data.csv'


        # デバッグ用コード追加
        print(f"self.directory: {self.directory}")
        print(f"input_csv: {input_csv}")

        if self.directory is None or input_csv is None:
            raise ValueError("self.directory または input_csv が None になっています。適切な値を設定してください。")


        input_csv_path = os.path.join(self.directory, input_csv)


        # 出力CSVファイル名
        output_csv = 'S_month_optimized.csv'
        output_csv_path = os.path.join(self.directory, output_csv)




        # S_month.csvにoptimized_demandをセットする
        # optimized leaf_node以外を0 clearする


        #@ STOP
        # 最適化にもとづく供給配分 ここでは簡易的にon-offしているのみ
        # 本来であれば、最適化の供給配分を詳細に行うべき所
        #self.clear_s_values(limited_supply_nodes, input_csv_path, output_csv_path)


        input_csv = 'S_month_data.csv'
        output_csv = 'S_month_optimized.csv'

        input_csv_path = os.path.join(self.directory, input_csv)
        output_csv_path = os.path.join(self.directory, output_csv)

        self.clear_s_values(self.flowDict_opt, input_csv_path, output_csv_path)



        ## **************************************
        ## input_csv = 'S_month_optimized.csv' load_files & planning
        ## **************************************
        #
        self.load_data_files4opt()     # loading with 'S_month_optimized.csv'

        #
        self.plan_through_engines4opt()




        # **************************************
        # いままでの評価と描画系
        # **************************************




        # *********************
        # evaluation@241220
        # *********************
        #@241225 memo "root_node_out_opt"のtreeにはcs_xxxxがセットされていない
        self.update_evaluation_results4optimize()


        # *********************
        # network graph
        # *********************
        # STAY ORIGINAL PLAN
        # selfのhandle nameは、root_node_outboundで、root_node_out_optではない
        # 
        # グラフ描画関数を呼び出し  最適ルートを赤線で表示
        #
        # title revenue, profit, profit_ratio
        self.draw_network4opt(G, Gdm_structure, Gsp, pos_E2E, self.flowDict_opt)

        #self.draw_network4opt(G, Gdm, Gsp, pos_E2E, flowDict_dm, flowDict_sp, flowDict_opt)


        # *********************
        # PSI graph
        # *********************
        self.root.after(1000, self.show_psi_graph4opt)
        #self.root.after(1000, self.show_psi_graph)

        #@ ADD
        # パラメータの初期化と更新を呼び出し
        self.updated_parameters()
        #@ STOP
        #self.updated_parameters4opt()










    def demand_leveling(self):


        # Demand Leveling logic here
        print("Demand Leveling executed.")


        # *********************************
        # Demand LEVELing on shipping yard / with pre_production week
        # *********************************

        year_st  = 2020
        year_end = 2021

        year_st  = self.plan_year_st
        year_end = year_st + self.plan_range - 1

        pre_prod_week = self.pre_proc_LT

        # STOP
        #year_st = df_capa_year["year"].min()
        #year_end = df_capa_year["year"].max()

        # root_node_outboundのsupplyの"S"のみを平準化して生成している
        demand_leveling_on_ship(self.root_node_outbound, pre_prod_week, year_st, year_end)


        # root_node_outboundのsupplyの"PSI"を生成している
        ##@241114 KEY CODE
        self.root_node_outbound.calcS2P_4supply()  #mother plantのconfirm S=> P
        self.root_node_outbound.calcPS2I4supply()  #mother plantのPS=>I


        #@241114 KEY CODE
        # ***************************************
        # その3　都度のparent searchを実行 setPS_on_ship2node
        # ***************************************
        feedback_psi_lists(self.root_node_outbound, self.nodes_outbound)


        #feedback_psi_lists(self.root_node_outbound, node_psi_dict_Ot4Sp, self.nodes_outbound)


        # STOP
        #decouple_node_names = [] # initial PUSH with NO decouple node
        ##push_pull_on_decouple
        #push_pull_all_psi2i_decouple4supply5(
        #    self.root_node_outbound,
        #    decouple_node_names )



        #@241114 KEY CODE
        #@240903

        #calc_all_psi2i4demand(self.root_node_outbound)
        #calc_all_psi2i4supply(self.root_node_outbound)


        self.update_evaluation_results()

        # PSI計画の初期状態をバックアップ
        self.psi_backup_to_file(self.root_node_outbound, 'psi_backup.pkl')


        self.view_nx_matlib()

        

        self.root.after(1000, self.show_psi("outbound", "supply"))
        #self.root.after(1000, self.show_psi_graph)



    def psi_backup(self, node, status_name):
        return copy.deepcopy(node)

    def psi_restore(self, node_backup, status_name):
        return copy.deepcopy(node_backup)

    def psi_backup_to_file(self, node, filename):
        with open(filename, 'wb') as file:
            pickle.dump(node, file)

    def psi_restore_from_file(self, filename):
        with open(filename, 'rb') as file:
            node_backup = pickle.load(file)
        return node_backup



# ****************
# an image of data
# ****************
#nodes_decouple_all [['MUC_N', 'MUC_D', 'MUC_I', 'HAM_N', 'HAM_D', 'HAM_I', 'FRALEAF', 'SHA_N', 'SHA_D', 'SHA_I', 'CAN_N', 'CAN_D', 'CAN_I'], ['MUC', 'HAM_N', 'HAM_D', 'HAM_I', 'FRALEAF', 'SHA_N', 'SHA_D', 'SHA_I', 'CAN_N', 'CAN_D', 'CAN_I'], ['SHA_N', 'SHA_D', 'SHA_I', 'CAN_N', 'CAN_D', 'CAN_I', 'HAM'], ['CAN_N', 'CAN_D', 'CAN_I', 'SHA', 'HAM'], ['CAN', 'SHA', 'HAM'], ['JPN']]
#
#nodes_decouple 0 ['MUC_N', 'MUC_D', 'MUC_I', 'HAM_N', 'HAM_D', 'HAM_I', 'FRALEAF', 'SHA_N', 'SHA_D', 'SHA_I', 'CAN_N', 'CAN_D', 'CAN_I']
#nodes_decouple 1 ['MUC', 'HAM_N', 'HAM_D', 'HAM_I', 'FRALEAF', 'SHA_N', 'SHA_D', 'SHA_I', 'CAN_N', 'CAN_D', 'CAN_I']
#nodes_decouple 2 ['SHA_N', 'SHA_D', 'SHA_I', 'CAN_N', 'CAN_D', 'CAN_I', 'HAM']
#nodes_decouple 3 ['CAN_N', 'CAN_D', 'CAN_I', 'SHA', 'HAM']
#nodes_decouple 4 ['CAN', 'SHA', 'HAM']



    def supply_planning(self):

        # Implement foreward planning logic here
        print("Supply planning with Decoupling points")


        #@241208 STOP seach nodes_decouple_all[-2] that is "DAD" nodes
        #nodes_decouple_all = make_nodes_decouple_all(self.root_node_outbound)
        #print("nodes_decouple_all", nodes_decouple_all)
        #
        #
        ## [-2] will be "DAD" node that is point of Delivery and Distribution
        #decouple_node_names = nodes_decouple_all[-2]

        self.root_node_outbound = self.psi_restore_from_file('psi_backup.pkl')

        if self.decouple_node_selected == []:

            #@241208 STOP RUNseach nodes_decouple_all[-2] that is "DAD" nodes
            nodes_decouple_all = make_nodes_decouple_all(self.root_node_outbound)
            print("nodes_decouple_all", nodes_decouple_all)

            #[-2] will be "DAD" node that is point of Delivery and Distribution
            decouple_node_names = nodes_decouple_all[-2]

        else:
            decouple_node_names = self.decouple_node_selected

        push_pull_all_psi2i_decouple4supply5(
            self.root_node_outbound, decouple_node_names )


        # eval area
        self.update_evaluation_results()


        # network area
        self.decouple_node_selected = decouple_node_names
        self.view_nx_matlib4opt()
        #self.view_nx_matlib()


        # PSI area
        self.root.after(1000, self.show_psi("outbound", "supply"))


        ## ツリーの簡単な可視化
        #show_tree(self.root_node_outbound)





























    def eval_buffer_stock(self):
        print("Supply planning with Decoupling points")


        # This backup is in "demand leveling"
        ## PSI計画の初期状態をバックアップ
        #self.psi_backup_to_file(self.root_node_outbound, 'psi_backup.pkl')


        nodes_decouple_all = make_nodes_decouple_all(self.root_node_outbound)
        print("nodes_decouple_all", nodes_decouple_all)

        for i, decouple_node_names in enumerate(nodes_decouple_all):
            print("nodes_decouple_all", nodes_decouple_all)


            # PSI計画の状態をリストア
            self.root_node_outbound = self.psi_restore_from_file('psi_backup.pkl')

            push_pull_all_psi2i_decouple4supply5(self.root_node_outbound, decouple_node_names)
            self.update_evaluation_results()

            print("decouple_node_names", decouple_node_names)
            print("self.total_revenue", self.total_revenue)
            print("self.total_profit", self.total_profit)

            self.decouple_node_dic[i] = [self.total_revenue, self.total_profit, decouple_node_names]

            ## network area
            #self.view_nx_matlib()

            ##@241207 TEST
            #self.root.after(1000, self.show_psi("outbound", "supply"))


        self.display_decoupling_patterns()
        # PSI area => move to selected_node in window




    def plan_through_engines4opt(self):

    #@RENAME
    # nodes_out_opt     : nodes_out_opt    
    # root_node_out_opt : root_node_out_opt


        print("planning with OPTIMIZED S")


        # Demand planning
        calc_all_psi2i4demand(self.root_node_out_opt)


        # Demand LEVELing on shipping yard / with pre_production week
        year_st = self.plan_year_st
        year_end = year_st + self.plan_range - 1
        pre_prod_week = self.pre_proc_LT
        demand_leveling_on_ship(self.root_node_out_opt, pre_prod_week, year_st, year_end)
        # root_node_out_optのsupplyの"PSI"を生成している
        self.root_node_out_opt.calcS2P_4supply()  #mother plantのconfirm S=> P
        self.root_node_out_opt.calcPS2I4supply()  #mother plantのPS=>I

        # ***************************************
        # その3　都度のparent searchを実行 setPS_on_ship2node
        # ***************************************
        feedback_psi_lists(self.root_node_out_opt, self.nodes_out_opt)



        #@241208 STOP
        ## Supply planning
        #print("Supply planning with Decoupling points")
        #nodes_decouple_all = make_nodes_decouple_all(self.root_node_out_opt)
        #print("nodes_decouple_all", nodes_decouple_all)
        #
        #for i, decouple_node_names in enumerate(nodes_decouple_all):
        #    decouple_flag = "OFF"
        #    if i == 0:

        decouple_node_names = self.decouple_node_selected

        push_pull_all_psi2i_decouple4supply5(self.root_node_out_opt, decouple_node_names)









    # *************************
    # show_psi
    # *************************
    def show_psi(self, bound, layer):
        print("making PSI graph data...")
    
        week_start = 1
        week_end = self.plan_range * 53
    
        psi_data = []
    
        if bound not in ["outbound", "inbound"]:
            print("error: outbound or inbound must be defined for PSI layer")
            return
    
        if layer not in ["demand", "supply"]:
            print("error: demand or supply must be defined for PSI layer")
            return
    
        def traverse_nodes(node):
            for child in node.children:
                traverse_nodes(child)
            collect_psi_data(node, layer, week_start, week_end, psi_data)
    
        if bound == "outbound":
            traverse_nodes(self.root_node_outbound)
        else:
            traverse_nodes(self.root_node_inbound)
    
        fig, axs = plt.subplots(len(psi_data), 1, figsize=(5, len(psi_data) * 1))  # figsizeの高さをさらに短く設定
    
        if len(psi_data) == 1:
            axs = [axs]

        for ax, (node_name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S) in zip(axs, psi_data):
            ax2 = ax.twinx()
    
            ax.bar(line_plot_data_2I.index, line_plot_data_2I.values, color='r', alpha=0.6)
            ax.bar(bar_plot_data_3P.index, bar_plot_data_3P.values, color='g', alpha=0.6)
            ax2.plot(bar_plot_data_0S.index, bar_plot_data_0S.values, color='b')
    
            ax.set_ylabel('I&P Lots', fontsize=8)
            ax2.set_ylabel('S Lots', fontsize=8)
            ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)
    
        fig.tight_layout(pad=0.5)
    
        print("making PSI figure and widget...")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
        canvas_psi = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_psi.draw()
        canvas_psi.get_tk_widget().pack(fill=tk.BOTH, expand=True)




    def show_psi_graph(self):
        print("making PSI graph data...")

        week_start = 1
        week_end = self.plan_range * 53

        psi_data = []

        def traverse_nodes(node):
            for child in node.children:
                traverse_nodes(child)
            collect_psi_data(node, "demand", week_start, week_end, psi_data)

        # ***************************
        # ROOT HANDLE
        # ***************************
        traverse_nodes(self.root_node_outbound)

        fig, axs = plt.subplots(len(psi_data), 1, figsize=(5, len(psi_data) * 1))  # figsizeの高さをさらに短く設定

        if len(psi_data) == 1:
            axs = [axs]

        for ax, (node_name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S) in zip(axs, psi_data):
            ax2 = ax.twinx()

            ax.bar(line_plot_data_2I.index, line_plot_data_2I.values, color='r', alpha=0.6)
            ax.bar(bar_plot_data_3P.index, bar_plot_data_3P.values, color='g', alpha=0.6)
            ax2.plot(bar_plot_data_0S.index, bar_plot_data_0S.values, color='b')

            ax.set_ylabel('I&P Lots', fontsize=8)
            ax2.set_ylabel('S Lots', fontsize=8)
            ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)

            # Y軸の整数設定
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        fig.tight_layout(pad=0.5)

        print("making PSI figure and widget...")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        canvas_psi = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_psi.draw()
        canvas_psi.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    #@241225 marked revenueとprofitは、node classにインスタンスあり
    def show_psi_graph4opt(self):
        print("making PSI graph data...")

        week_start = 1
        week_end = self.plan_range * 53

        psi_data = []

        nodes_outbound = self.nodes_outbound  # node辞書{}

        def traverse_nodes(node_opt):
            for child in node_opt.children:
                print("show_psi_graph4opt child.name", child.name)
                traverse_nodes(child)
            node_out = nodes_outbound[node_opt.name]
            collect_psi_data_opt(node_opt, node_out, "supply", week_start, week_end, psi_data)

        # ***************************
        # change ROOT HANDLE
        # ***************************
        traverse_nodes(self.root_node_out_opt)

        fig, axs = plt.subplots(len(psi_data), 1, figsize=(5, len(psi_data) * 1))  # figsizeの高さをさらに短く設定

        if len(psi_data) == 1:
            axs = [axs]

        for ax, (node_name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S) in zip(axs, psi_data):
            ax2 = ax.twinx()

            ax.bar(line_plot_data_2I.index, line_plot_data_2I.values, color='r', alpha=0.6)
            ax.bar(bar_plot_data_3P.index, bar_plot_data_3P.values, color='g', alpha=0.6)
            ax2.plot(bar_plot_data_0S.index, bar_plot_data_0S.values, color='b')

            ax.set_ylabel('I&P Lots', fontsize=8)
            ax2.set_ylabel('S Lots', fontsize=8)
            ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)

            # Y軸の整数設定
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        fig.tight_layout(pad=0.5)

        print("making PSI figure and widget...")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        canvas_psi = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_psi.draw()
        canvas_psi.get_tk_widget().pack(fill=tk.BOTH, expand=True)




    def show_psi_graph_OLD(self):
        print("making PSI graph data...")
    
        week_start = 1
        week_end = self.plan_range * 53
    
        psi_data = []
    
        def traverse_nodes(node):
            for child in node.children:
                traverse_nodes(child)
            collect_psi_data(node, "demand", week_start, week_end, psi_data)


        # ***************************
        # ROOT HANDLE
        # ***************************
        traverse_nodes(self.root_node_outbound)
    


        fig, axs = plt.subplots(len(psi_data), 1, figsize=(5, len(psi_data) * 1))  # figsizeの高さをさらに短く設定
    
        if len(psi_data) == 1:
            axs = [axs]
    
        for ax, (node_name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S) in zip(axs, psi_data):
            ax2 = ax.twinx()
    
            ax.bar(line_plot_data_2I.index, line_plot_data_2I.values, color='r', alpha=0.6)
            ax.bar(bar_plot_data_3P.index, bar_plot_data_3P.values, color='g', alpha=0.6)
            ax2.plot(bar_plot_data_0S.index, bar_plot_data_0S.values, color='b')
    
            ax.set_ylabel('I&P Lots', fontsize=8)
            ax2.set_ylabel('S Lots', fontsize=8)
            ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)

        fig.tight_layout(pad=0.5)

        print("making PSI figure and widget...")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
        canvas_psi = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_psi.draw()
        canvas_psi.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    
    
    
    #@241225 marked revenueとprofitは、node classにインスタンスあり
    def show_psi_graph4opt_OLD(self):
        print("making PSI graph data...")
    
        week_start = 1
        week_end = self.plan_range * 53
    
        psi_data = []
    
        nodes_outbound = self.nodes_outbound  # node辞書{}


        def traverse_nodes(node_opt):
            for child in node_opt.children:
                print("show_psi_graph4opt child.name", child.name)
                traverse_nodes(child)
            node_out = nodes_outbound[node_opt.name]
            collect_psi_data_opt(node_opt, node_out, "supply", week_start, week_end, psi_data)
            #collect_psi_data(node, "demand", week_start, week_end, psi_data)


        # ***************************
        # change ROOT HANDLE
        # ***************************
        traverse_nodes(self.root_node_out_opt)
        #traverse_nodes(self.root_node_outbound)
    


        fig, axs = plt.subplots(len(psi_data), 1, figsize=(5, len(psi_data) * 1))  # figsizeの高さをさらに短く設定
    
        if len(psi_data) == 1:
            axs = [axs]
    
        for ax, (node_name, revenue, profit, profit_ratio, line_plot_data_2I, bar_plot_data_3P, bar_plot_data_0S) in zip(axs, psi_data):
            ax2 = ax.twinx()
    
            ax.bar(line_plot_data_2I.index, line_plot_data_2I.values, color='r', alpha=0.6)
            ax.bar(bar_plot_data_3P.index, bar_plot_data_3P.values, color='g', alpha=0.6)
            ax2.plot(bar_plot_data_0S.index, bar_plot_data_0S.values, color='b')
    
            ax.set_ylabel('I&P Lots', fontsize=8)
            ax2.set_ylabel('S Lots', fontsize=8)
            ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)

        fig.tight_layout(pad=0.5)

        print("making PSI figure and widget...")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
        canvas_psi = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_psi.draw()
        canvas_psi.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    




    # ***************************
    # make network with NetworkX
    # ***************************



    def show_network_E2E_matplotlib(self,
            root_node_outbound, nodes_outbound, 
            root_node_inbound, nodes_inbound, 
            G, Gdm, Gsp):
        
        # Original code's logic to process and set up the network
        root_node_name_out = root_node_outbound.name 
        root_node_name_in  = root_node_inbound.name

        total_demand =0
        total_demand = set_leaf_demand(root_node_outbound, total_demand)
        #total_demand = self.set_leaf_demand(root_node_outbound, total_demand)
        print("average_total_demand", total_demand)
        print("root_node_outbound.nx_demand", root_node_outbound.nx_demand)

        root_node_outbound.nx_demand = total_demand  
        root_node_inbound.nx_demand = total_demand  

        G_add_nodes_from_tree(root_node_outbound, G)
        #self.G_add_nodes_from_tree(root_node_outbound, G)
        G_add_nodes_from_tree_skip_root(root_node_inbound, root_node_name_in, G)
        #self.G_add_nodes_from_tree_skip_root(root_node_inbound, root_node_name_in, G)

        G.add_node("sales_office", demand=total_demand)
        G.add_node(root_node_outbound.name, demand=0)
        G.add_node("procurement_office", demand=(-1 * total_demand))

        G_add_edge_from_tree(root_node_outbound, G)
        #self.G_add_edge_from_tree(root_node_outbound, G)
        supplyers_capacity = root_node_inbound.nx_demand * 2 
        G_add_edge_from_inbound_tree(root_node_inbound, supplyers_capacity, G)
        #self.G_add_edge_from_inbound_tree(root_node_inbound, supplyers_capacity, G)

        G_add_nodes_from_tree(root_node_outbound, Gdm)
        #self.G_add_nodes_from_tree(root_node_outbound, Gdm)
        Gdm.add_node(root_node_outbound.name, demand = (-1 * total_demand))
        Gdm.add_node("sales_office", demand = total_demand)
        Gdm_add_edge_sc2nx_outbound(root_node_outbound, Gdm)
        #self.Gdm_add_edge_sc2nx_outbound(root_node_outbound, Gdm)

        G_add_nodes_from_tree(root_node_inbound, Gsp)
        #self.G_add_nodes_from_tree(root_node_inbound, Gsp)
        Gsp.add_node("procurement_office", demand = (-1 * total_demand))
        Gsp.add_node(root_node_inbound.name, demand = total_demand)
        Gsp_add_edge_sc2nx_inbound(root_node_inbound, Gsp)
        #self.Gsp_add_edge_sc2nx_inbound(root_node_inbound, Gsp)

        pos_E2E = make_E2E_positions(root_node_outbound, root_node_inbound)
        #pos_E2E = self.make_E2E_positions(root_node_outbound, root_node_inbound)
        pos_E2E = tune_hammock(pos_E2E, nodes_outbound, nodes_inbound)
        #pos_E2E = self.tune_hammock(pos_E2E, nodes_outbound, nodes_inbound)

        return pos_E2E, G, Gdm, Gsp



    def view_nx_matlib4load(self):

        
        #self.ax_network.clear()

        G = nx.DiGraph()
        Gdm_structure = nx.DiGraph()
        Gsp = nx.DiGraph()

        #G = self.G
        #Gdm_structure = self.Gdm_structure
        #Gsp = self.Gsp

        #@241211 ADD
        # まっさらにG系を作り直す処理を流す???


        pos_E2E, G, Gdm, Gsp = self.show_network_E2E_matplotlib(
            self.root_node_outbound, self.nodes_outbound,
            self.root_node_inbound, self.nodes_inbound,
            G, Gdm_structure, Gsp
        )

        self.pos_E2E = pos_E2E
        print(f"view_nx_matlib self.decouple_node_selected: {self.decouple_node_selected}")
        self.draw_network(G, Gdm, Gsp, pos_E2E)




    def view_nx_matlib(self):
        G = nx.DiGraph()
        Gdm_structure = nx.DiGraph()
        Gsp = nx.DiGraph()

        print(f"view_nx_matlib before show_network_E2E_matplotlib self.decouple_node_selected: {self.decouple_node_selected}")

        pos_E2E, G, Gdm_structure, Gsp = self.show_network_E2E_matplotlib(
            self.root_node_outbound, self.nodes_outbound,
            self.root_node_inbound, self.nodes_inbound,
            G, Gdm_structure, Gsp
        )

        self.pos_E2E = pos_E2E

        print(f"view_nx_matlib after show_network_E2E_matplotlib self.decouple_node_selected: {self.decouple_node_selected}")

        self.G = G
        self.Gdm_structure = Gdm_structure
        self.Gsp = Gsp

        self.draw_network(self.G, self.Gdm_structure, self.Gsp, self.pos_E2E)



    def draw_network(self, G, Gdm, Gsp, pos_E2E):
        self.ax_network.clear()  # 図をクリア

        # 評価結果の更新
        ttl_revenue = self.total_revenue
        ttl_profit = self.total_profit
        ttl_profit_ratio = (ttl_profit / ttl_revenue) if ttl_revenue != 0 else 0

        # 四捨五入して表示
        total_revenue = round(ttl_revenue)
        total_profit = round(ttl_profit)
        profit_ratio = round(ttl_profit_ratio * 100, 1)  # パーセント表示

        # タイトルを設定
        self.ax_network.set_title(f'PySI\nOptimized Supply Chain Network\nREVENUE: {total_revenue:,} | PROFIT: {total_profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=10)

        self.ax_network.axis('off')

        print("draw_network self.decouple_node_selected", self.decouple_node_selected)
        print("draw_network G nodes", list(G.nodes()))
        print("draw_network G edges", list(G.edges()))

        # Node描画
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]

        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):
            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax_network)

        # Edge描画
        for edge in G.edges():
            edge_color = 'lightgrey' if edge[0] == "procurement_office" or edge[1] == "sales_office" else 'blue' if edge in Gdm.edges() else 'green' if edge in Gsp.edges() else 'gray'
            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax_network, width=0.5)

        # Labels描画
        node_labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax_network)


        #@ STOP
        ## キャンバスの再描画
        #self.canvas_network.draw()

        # キャンバスの再描画
        # 描画処理を待機キューに入れて部分的な描画を実行
        self.canvas_network.draw_idle()



    def draw_network_OLDOLD(self, G, Gdm, Gsp, pos_E2E):

        #self.ax.clear()  # 図をクリア
        self.ax_network.clear()  # 図をクリア


        # 評価結果の更新
        ttl_revenue = self.total_revenue
        ttl_profit = self.total_profit
        ttl_profit_ratio = (ttl_profit / ttl_revenue) if ttl_revenue != 0 else 0

        # 四捨五入して表示
        total_revenue = round(ttl_revenue)
        total_profit = round(ttl_profit)
        profit_ratio = round(ttl_profit_ratio * 100, 1)  # パーセント表示

        # タイトルを設定
        self.ax.set_title(f'PySI\nOptimized Supply Chain Network\nREVENUE: {total_revenue:,} | PROFIT: {total_profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=10)

        self.ax.axis('off')

        print("draw_network self.decouple_node_selected", self.decouple_node_selected)
        print("draw_network G nodes", list(G.nodes()))
        print("draw_network G edges", list(G.edges()))

        # Node描画
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]

        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):
            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax)

        # Edge描画
        for edge in G.edges():
            edge_color = 'lightgrey' if edge[0] == "procurement_office" or edge[1] == "sales_office" else 'blue' if edge in Gdm.edges() else 'green' if edge in Gsp.edges() else 'gray'
            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax, width=0.5)

        # Labels描画
        node_labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax)


        #@ STOP
        # キャンバスの再描画
        self.canvas_network.draw()







    def view_nx_matlib_OLD(self):

        G = nx.DiGraph()
        Gdm_structure = nx.DiGraph()
        Gsp = nx.DiGraph()

        print(f"view_nx_matlib before show_network_E2E_matplotlib self.decouple_node_selected: {self.decouple_node_selected}")

        pos_E2E, G, Gdm_structure, Gsp = self.show_network_E2E_matplotlib(
            self.root_node_outbound, self.nodes_outbound,
            self.root_node_inbound, self.nodes_inbound,
            G, Gdm_structure, Gsp
        )

        self.pos_E2E = pos_E2E

        print(f"view_nx_matlib after show_network_E2E_matplotlib self.decouple_node_selected: {self.decouple_node_selected}")

        self.G = G
        self.Gdm_structure = Gdm_structure
        self.Gsp = Gsp

        self.draw_network(G, Gdm_structure, Gsp, pos_E2E)

        #@241221 STOP
        #self.draw_network4opt(G,Gdm_structure, Gsp, pos_E2E,self.flowDict_opt)


        ## 追加: キャンバスを再描画
        #self.canvas_network.draw()



    def draw_network_OLD(self, G, Gdm, Gsp, pos_E2E):
        self.ax_network.clear()  # 図をクリア

        # 評価結果の更新
        ttl_revenue = self.total_revenue
        ttl_profit = self.total_profit
        ttl_profit_ratio = (ttl_profit / ttl_revenue) if ttl_revenue != 0 else 0

        # 四捨五入して表示
        total_revenue = round(ttl_revenue)
        total_profit = round(ttl_profit)
        profit_ratio = round(ttl_profit_ratio * 100, 1)  # パーセント表示


        #ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)


        # タイトルを設定
        self.ax_network.set_title(f'PySI\nOptimized Supply Chain Network\nREVENUE: {total_revenue:,} | PROFIT: {total_profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=10)


#".format(total_revenue, total_profit))


        self.ax_network.axis('off')

        print("draw_network self.decouple_node_selected", self.decouple_node_selected)
        print("draw_network G nodes", list(G.nodes()))
        print("draw_network G edges", list(G.edges()))


        # node
        print("preparing node data")
        # node
        # Define the shapes and colors based on decouple_node_selected
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]

        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):
            print("draw_network node, shape, color", node, shape, color)
            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax_network)


        # edge
        print("preparing edge data")
        # edge
        for edge in G.edges():
            if edge[0] == "procurement_office" or edge[1] == "sales_office":
                edge_color = 'lightgrey'  # "procurement_office"または"sales_office"に接続するエッジはlightgrey
            elif edge in Gdm.edges():
                edge_color = 'blue'
            elif edge in Gsp.edges():
                edge_color = 'green'
            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax_network, width=0.5)


        # labels
        print("preparing labels data")
        # labels
        node_labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax_network)


        # キャンバスの再描画はココで、view_nx_matlibで行うのはSTOP
        self.canvas_network.draw()







    def view_nx_matlib4opt(self):
        G = nx.DiGraph()
        Gdm_structure = nx.DiGraph()
        Gsp = nx.DiGraph()

        self.G = G
        self.Gdm_structure = Gdm_structure
        self.Gsp = Gsp

        pos_E2E, G, Gdm, Gsp = self.show_network_E2E_matplotlib(
            self.root_node_outbound, self.nodes_outbound,
            self.root_node_inbound, self.nodes_inbound,
            G, Gdm_structure, Gsp
        )

        self.pos_E2E = pos_E2E

        #self.draw_network4opt(G, Gdm, Gsp, pos_E2E)

        # グラフ描画関数を呼び出し  最適ルートを赤線で表示

        print("load_from_directory self.flowDict_opt", self.flowDict_opt)

        self.draw_network4opt(G, Gdm_structure, Gsp, pos_E2E, self.flowDict_opt)


    def draw_network4opt(self, G, Gdm, Gsp, pos_E2E, flowDict_opt):

        ## 既存の軸をクリア
        #self.ax_network.clear()

    #def draw_network(self, G, Gdm, Gsp, pos_E2E):

        self.ax_network.clear()  # 図をクリア


        print("draw_network4opt: self.total_revenue", self.total_revenue)
        print("draw_network4opt: self.total_profit", self.total_profit)

        # 評価結果の更新
        ttl_revenue = self.total_revenue
        ttl_profit = self.total_profit
        ttl_profit_ratio = (ttl_profit / ttl_revenue) if ttl_revenue != 0 else 0

        # 四捨五入して表示
        total_revenue = round(ttl_revenue)
        total_profit = round(ttl_profit)
        profit_ratio = round(ttl_profit_ratio * 100, 1)  # パーセント表示


        #ax.set_title(f'Node: {node_name} | REVENUE: {revenue:,} | PROFIT: {profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=8)


        # タイトルを設定
        self.ax_network.set_title(f'PySI\nOptimized Supply Chain Network\nREVENUE: {total_revenue:,} | PROFIT: {total_profit:,} | PROFIT_RATIO: {profit_ratio}%', fontsize=10)


        print("ax_network.set_title: total_revenue", total_revenue)
        print("ax_network.set_title: total_profit", total_profit)


#".format(total_revenue, total_profit))


        self.ax_network.axis('off')








        # ノードの形状と色を定義
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]


        # ノードの描画
        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):

            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax_network)


        # エッジの描画
        for edge in G.edges():
            if edge[0] == "procurement_office" or edge[1] == "sales_office":
                edge_color = 'lightgrey'  # "procurement_office"または"sales_office"に接続するエッジはlightgrey
            elif edge in Gdm.edges():
                edge_color = 'blue'  # outbound（Gdm）のエッジは青
            elif edge in Gsp.edges():
                edge_color = 'green'  # inbound（Gsp）のエッジは緑
            else:
                edge_color = 'lightgrey'  # その他はlightgrey

            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax_network, width=0.5)

        # 最適化pathの赤線表示
        for from_node, flows in flowDict_opt.items():
            for to_node, flow in flows.items():
                if flow > 0:
                    # "G"の上に描画
                    nx.draw_networkx_edges(self.G, self.pos_E2E, edgelist=[(from_node, to_node)], ax=self.ax_network, edge_color='red', arrows=False, width=0.5)

        # ノードラベルの描画
        node_labels = {node: f"{node}" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax_network)





        # ***************************
        # title and axis
        # ***************************
        #plt.title("Supply Chain Network end2end")

        #@ STOOOOOOOP
        #plt.title("Optimized Supply Chain Network")
        #self.ax_network.axis('off')  # 軸を非表示にする


        # キャンバスを更新
        self.canvas_network.draw()



    def draw_network_OLD(self, G, Gdm, Gsp, pos_E2E):

        #@241212 STOP
        #self.ax_network.clear()





        ## Eval for title
        #self.update_evaluation_results()


        ttl_revenue = self.total_revenue
        ttl_profit  = self.total_profit

        if ttl_revenue == 0:
            ttl_profit_ratio = 0
        else:
            ttl_profit_ratio = ttl_profit / ttl_revenue

        # 四捨五入して表示 
        total_revenue = round(ttl_revenue) 
        total_profit = round(ttl_profit) 
        profit_ratio = round(ttl_profit_ratio*100, 1) # パーセント表示

        plt.title("PySI\nOptimized Supply Chain Network\nRevenue: {} Profit: {}".format( total_revenue, total_profit))

        #plt.title("PySI\nOptimized Supply Chain Network\nRevenue: {} Profit: {}".format( self.total_revenue, self.total_profit))



        self.ax_network.axis('off')


        print("draw_network self.decouple_node_selected", self.decouple_node_selected)
        print("draw_network G nodes", list(G.nodes()))
        print("draw_network G edges", list(G.edges()))

        # Define the shapes and colors based on decouple_node_selected
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]


        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):

            print("draw_network node, shape, color", node, shape, color)

            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax_network)

        for edge in G.edges():
            if edge[0] == "procurement_office" or edge[1] == "sales_office":
                edge_color = 'lightgrey'  # "procurement_office"または"sales_office"に接続するエッジはlightgrey
            elif edge in Gdm.edges():
                edge_color = 'blue'
            elif edge in Gsp.edges():
                edge_color = 'green'

            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax_network, width=0.5)


        node_labels = {node: node for node in G.nodes()}

        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax_network)




        ##print("Before canvas_network.draw()")
        ### キャンバスの再描画
        self.canvas_network.draw()
        ##print("After canvas_network.draw()")



    def draw_network_OLD(self, G, Gdm, Gsp, pos_E2E):

        self.ax_network.clear()

        print("draw_network self.decouple_node_selected", self.decouple_node_selected)
        print("draw_network G nodes", list(G.nodes()))
        print("draw_network G edges", list(G.edges()))


        # Define the shapes and colors based on decouple_node_selected
        node_shapes = ['v' if node in self.decouple_node_selected else 'o' for node in G.nodes()]
        node_colors = ['brown' if node in self.decouple_node_selected else 'lightblue' for node in G.nodes()]

        for node, shape, color in zip(G.nodes(), node_shapes, node_colors):

            print("draw_network node, shape, color", node, shape, color)


            nx.draw_networkx_nodes(G, pos_E2E, nodelist=[node], node_size=50, node_color=color, node_shape=shape, ax=self.ax_network)



        for edge in G.edges():
            if edge[0] == "procurement_office" or edge[1] == "sales_office":
                edge_color = 'lightgrey'  # "procurement_office"または"sales_office"に接続するエッジはlightgrey
            elif edge in Gdm.edges():
                edge_color = 'blue'
            elif edge in Gsp.edges():
                edge_color = 'green'
            nx.draw_networkx_edges(G, pos_E2E, edgelist=[edge], edge_color=edge_color, arrows=False, ax=self.ax_network, width=0.5)

        node_labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos_E2E, labels=node_labels, font_size=6, ax=self.ax_network)

        plt.title("Optimized Supply Chain Network\nRevenue: {} Profit: {}".format(self.total_revenue, self.total_profit))

        self.ax_network.axis('off')

        # キャンバスの再描画

        self.canvas_network.draw()









    def show_network_E2E_matplotlib(
            self, root_node_outbound, nodes_outbound, 
            root_node_inbound, nodes_inbound, 
            G, Gdm, Gsp):
        
        root_node_name_out = root_node_outbound.name 
        root_node_name_in  = root_node_inbound.name

        total_demand =0
        total_demand = set_leaf_demand(root_node_outbound, total_demand)
        print("average_total_demand", total_demand)
        print("root_node_outbound.nx_demand", root_node_outbound.nx_demand)

        root_node_outbound.nx_demand = total_demand  
        root_node_inbound.nx_demand = total_demand  

        G_add_nodes_from_tree(root_node_outbound, G)
        G_add_nodes_from_tree_skip_root(root_node_inbound, root_node_name_in, G)

        G.add_node("sales_office", demand=total_demand)
        G.add_node(root_node_outbound.name, demand=0)
        G.add_node("procurement_office", demand=(-1 * total_demand))

        G_add_edge_from_tree(root_node_outbound, G)
        supplyers_capacity = root_node_inbound.nx_demand * 2 
        G_add_edge_from_inbound_tree(root_node_inbound, supplyers_capacity, G)

        G_add_nodes_from_tree(root_node_outbound, Gdm)
        Gdm.add_node(root_node_outbound.name, demand = (-1 * total_demand))
        Gdm.add_node("sales_office", demand = total_demand)
        Gdm_add_edge_sc2nx_outbound(root_node_outbound, Gdm)

        G_add_nodes_from_tree(root_node_inbound, Gsp)
        Gsp.add_node("procurement_office", demand = (-1 * total_demand))
        Gsp.add_node(root_node_inbound.name, demand = total_demand)
        Gsp_add_edge_sc2nx_inbound(root_node_inbound, Gsp)

        pos_E2E = make_E2E_positions(root_node_outbound, root_node_inbound)
        pos_E2E = tune_hammock(pos_E2E, nodes_outbound, nodes_inbound)

        return pos_E2E, G, Gdm, Gsp





    def display_decoupling_patterns(self):
        subroot = tk.Toplevel(self.root)
        subroot.title("Decoupling Stock Buffer Patterns")

        frame = ttk.Frame(subroot)
        frame.pack(fill='both', expand=True)

        tree = ttk.Treeview(frame, columns=('Revenue', 'Profit', 'Nodes'), show='headings')
        tree.heading('Revenue', text='Revenue')
        tree.heading('Profit', text='Profit')
        tree.heading('Nodes', text='Nodes')
        tree.pack(fill='both', expand=True)

        style = ttk.Style()
        # カラムヘッダを中央揃えにする
        style.configure('Treeview.Heading', anchor='center')

        style.configure('Treeview', rowheight=25)  # 行の高さを設定

        def format_number(value):
            return f"{round(value):,}"

        for i, (revenue, profit, nodes) in self.decouple_node_dic.items():
            formatted_revenue = format_number(revenue)
            formatted_profit = format_number(profit)
            tree.insert('', 'end', values=(formatted_revenue, formatted_profit, ', '.join(nodes)))

        # 列を右寄せに設定する関数
        def adjust_column(tree, col):
            tree.column(col, anchor='e')

        # Revenue と Profit の列を右寄せに設定
        adjust_column(tree, 'Revenue')
        adjust_column(tree, 'Profit')

        selected_pattern = None

        def on_select_pattern(event):
            nonlocal selected_pattern
            item = tree.selection()[0]
            selected_pattern = tree.item(item, 'values')

        tree.bind('<<TreeviewSelect>>', on_select_pattern)

        def on_confirm():
            if selected_pattern:
                self.decouple_node_selected = selected_pattern[2].split(', ')

                print("decouple_node_selected", self.decouple_node_selected)
                self.execute_selected_pattern()

                subroot.destroy()  # サブウィンドウを閉じる

        confirm_button = ttk.Button(subroot, text="SELECT buffering stock", command=on_confirm)
        confirm_button.pack()

        subroot.protocol("WM_DELETE_WINDOW", on_confirm)








    def execute_selected_pattern(self):
        decouple_node_names = self.decouple_node_selected

        # PSI計画の状態をリストア
        self.root_node_outbound = self.psi_restore_from_file('psi_backup.pkl')

        print("exe engine decouple_node_selected", self.decouple_node_selected)

        push_pull_all_psi2i_decouple4supply5(self.root_node_outbound, decouple_node_names)

        self.update_evaluation_results()

        self.view_nx_matlib()
        self.root.after(1000, self.show_psi("outbound", "supply"))




    def load4execute_selected_pattern(self):


        # 1. Load元となるdirectoryの問い合わせ
        load_directory = filedialog.askdirectory()
        if not load_directory:
            return  # ユーザーがキャンセルした場合

        ## 2. 初期処理のcsv fileのコピー
        #for filename in os.listdir(load_directory):
        #    if filename.endswith('.csv'):
        #        full_file_name = os.path.join(load_directory, filename)
        #        if os.path.isfile(full_file_name):
        #            shutil.copy(full_file_name, self.directory)

        # 3. Tree構造の読み込み
        with open(os.path.join(load_directory, 'root_node_outbound.pkl'), 'rb') as f:
            self.root_node_outbound = pickle.load(f)
            print(f"root_node_outbound loaded: {self.root_node_outbound.name}")

        #
        #with open(os.path.join(load_directory, 'root_node_inbound.pkl'), 'rb') as f:
        #    self.root_node_inbound = pickle.load(f)
        #    print(f"root_node_inbound loaded: {self.root_node_inbound}")

        # 4. PSIPlannerAppのデータ・インスタンスの読み込み
        with open(os.path.join(load_directory, 'psi_planner_app.pkl'), 'rb') as f:
            loaded_attributes = pickle.load(f)
            self.__dict__.update(loaded_attributes)
            print(f"loaded_attributes: {loaded_attributes}")

        ## 5. nodes_outboundとnodes_inboundを再生成
        #self.nodes_outbound = self.regenerate_nodes(self.root_node_outbound)
        #self.nodes_inbound = self.regenerate_nodes(self.root_node_inbound)

        # network area
        print("load_from_directory self.decouple_node_selected", self.decouple_node_selected)



        #decouple_node_names = self.decouple_node_selected





        decouple_node_names = self.decouple_node_selected

        ## PSI計画の状態をリストア
        #self.root_node_outbound = self.psi_restore_from_file('psi_backup.pkl')

        print("exe engine decouple_node_selected", self.decouple_node_selected)

        push_pull_all_psi2i_decouple4supply5(self.root_node_outbound, decouple_node_names)

        self.update_evaluation_results()


        #@241212 Gdm_structureにupdated
        self.draw_network(G, Gdm_structure, Gsp, pos_E2E)

        ## 追加: キャンバスを再描画
        #self.canvas_network.draw()
        #
        #self.view_nx_matlib()

        self.root.after(1000, self.show_psi("outbound", "supply"))




# ******************************************
# clear_s_values
# ******************************************
#
#複数年のデータに対応するために、node_name と year をキーにして各ノードのデータを処理。
#
#説明
#leaf_nodeの特定方法の修正：
#
#flow_dict 内で各ノードに sales_office が含まれているかどうかで leaf_nodes を特定します。
#
#rule-1, rule-2, rule-3 の適用：
#
#rule-1: flow_dict に存在しないノードの月次Sの値を0に設定。
#
#rule-2: flow_dict に存在し、sales_office に繋がるノードの値が0である場合、月次S#の値を0に設定。
#
#rule-3: flow_dict に存在し、sales_office に繋がるノードの値が0以外である場合、月次Sの値をプロポーションに応じて分配。
#
#proportionsの計算と値の丸め：
#
#各月のproportionを計算し、それを使って丸めた値を求めます。
#
#rounded_values に丸めた値を格納し、合計が期待する供給量と一致しない場合は、
#最大の値を持つ月で調整します。
#
#年間total_supplyが0の場合の処理：
#年間total_supplyが0の場合は、月次Sの値をすべて0に設定します。


    def clear_s_values(self, flow_dict, input_csv, output_csv):
        # 1. 入力ファイルS_month_data.csvをデータフレームに読み込み
        df = pd.read_csv(input_csv)

        # leaf_nodeを特定
        leaf_nodes = [node for node, connections in flow_dict.items() if 'sales_office' in connections]

        # 2. rule-1, rule-2, rule-3を適用してデータを修正する
        for index, row in df.iterrows():
            node_name = row['node_name']
            year = row['year']
            
            if node_name in flow_dict:
                # ノードがflow_dictに存在する場合
                if node_name in leaf_nodes:
                    # rule-2: ノードの値が0の場合、月次Sの値をすべて0に設定
                    if flow_dict[node_name]['sales_office'] == 0:
                        df.loc[(df['node_name'] == node_name) & (df['year'] == year),
                               ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']] = 0
                    else:
                        # rule-3: ノードの値が0以外の場合、月次Sのproportionに応じて分配
                        total_supply = sum(df.loc[(df['node_name'] == node_name) & (df['year'] == year), 
                                                  ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']].values.flatten())
                        if total_supply != 0:
                            proportions = df.loc[(df['node_name'] == node_name) & (df['year'] == year), 
                                                 ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']].values.flatten() / total_supply
                            rounded_values = [round(proportion * flow_dict[node_name]['sales_office']) for proportion in proportions]
                            difference = flow_dict[node_name]['sales_office'] - sum(rounded_values)
                            if difference != 0:
                                max_index = rounded_values.index(max(rounded_values))
                                rounded_values[max_index] += difference
                            df.loc[(df['node_name'] == node_name) & (df['year'] == year),
                                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']] = rounded_values
                        else:
                            # 供給量がゼロの場合、元データを保持（エラーチェック）
                            df.loc[(df['node_name'] == node_name) & (df['year'] == year), 
                                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']] = [0] * 12
            else:
                # rule-1: ノードがflow_dictに存在しない場合、月次Sの値をすべて0に設定
                df.loc[index, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']] = 0

        # 3. 結果を"S_month_data_optimized.csv"として保存する
        df.to_csv(output_csv, index=False)
        print(f"Optimized data saved to {output_csv}")





    def clear_s_values_OLD(self, limited_supply_nodes, input_csv, output_csv):
        # 1. 入力ファイルS_month_data.csvをdataframeに読込み
        df = pd.read_csv(input_csv)

        # 2. limited_supply_nodesの各要素node nameに該当する
        #    S_month_dataのSの値をすべて0 clearする。
        df.loc[df['node_name'].isin(limited_supply_nodes), ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12']] = 0
    
        # 3. 結果を"S_month_data_optimized.csv"として保存する
        df.to_csv(output_csv, index=False)
        print(f"Optimized data saved to {output_csv}")





    def load_plan_and_view_nx_matlib(self):

        G = nx.DiGraph()    # base display field
        Gdm_structure = nx.DiGraph()
        Gsp = nx.DiGraph()  # optimise for supply side


        self.G = G
        self.Gdm_structure = Gdm_structure
        self.Gsp = Gsp


        root_node_outbound = self.root_node_outbound 
        nodes_outbound = self.nodes_outbound     
        root_node_inbound = self.root_node_inbound  
        nodes_inbound = self.nodes_inbound      


        pos_E2E, G, Gdm_structure, Gsp = self.show_network_E2E_matplotlib(
            root_node_outbound, nodes_outbound, 
            root_node_inbound, nodes_inbound, 
            G, Gdm_structure, Gsp
        )


        # **************************************************
        # optimizing here
        # **************************************************

        G_opt = Gdm_structure.copy()

        # 最適化パラメータをリセット
        self.reset_optimization_params(G_opt)

        # 新しい最適化パラメータを設定
        self.set_optimization_params(G_opt)

        flowDict_opt = self.flowDict_opt
        print("optimizing here flowDict_opt", flowDict_opt)


        # 最適化を実行
        # fllowing set should be done here
        #self.flowDict_opt = flowDict_opt
        #self.flowCost_opt = flowCost_opt

        self.run_optimization(G_opt)

        # flowCost_opt = self.flowCost_opt # direct input

        G_result = G_opt.copy()


        G_view = G_result.copy()
        self.add_optimized_path(G_view, self.flowDict_opt)



        # 6. パラメータリセットとシミュレーション繰り返し

#        # 前回の最適化pathをリセット
#        self.reset_optimized_path(G_result)
#        
#        # 新しい最適化pathを追加
#        #G_result = G_opt.copy()
#        self.add_optimized_path(G_result, flowDict_opt)
#    
#        # 最適化pathの表示（オプション）
#        #print("Iteration", i + 1)
#        print("Optimized Path:", flowDict_opt)
#        print("Cost:", flowCost_opt)
#
#
#        G_view = G_result.copy()
#
#        # 修正後のコードでadd_optimized_pathを呼び出します
#        add_optimized_path(G_view, flow_dict)
#
#
#
        # 最適化パラメータをリセット
        self.reset_optimization_params(G_opt)
        
        # 新しい最適化パラメータを設定
        self.set_optimization_params(G_opt)
        
        # 最適化を実行
        # fllowing set should be done here
        #self.flowDict_opt = flowDict_opt
        #self.flowCost_opt = flowCost_opt

        self.run_optimization(G_opt)
        print("run_optimization self.flowDict_opt", self.flowDict_opt)



        #@241205 STOP **** flowDict_optを使ったGのE2Eの表示系に任せる
        ## 前回の最適化pathをリセット
        self.reset_optimized_path(G_result)
        #
        ## 新しい最適化pathを追加
        G_result = G_opt.copy()
        self.add_optimized_path(G_result, self.flowDict_opt)
        
        # 最適化pathの表示（オプション）
        #print("Iteration", i + 1)
        print("Optimized Path:", self.flowDict_opt)
        print("Optimized Cost:", self.flowCost_opt)


        # make optimized tree and PSI planning and show it
        flowDict_opt = self.flowDict_opt

        optimized_nodes = self.create_optimized_tree(flowDict_opt)


        if not optimized_nodes:
            error_message = "error: optimization with NOT enough supply"
            print(error_message)
            self.show_error_message(error_message)  # 画面にエラーメッセージを表示する関数
            return


        print("optimized_nodes", optimized_nodes)
        optimized_root = optimized_nodes['supply_point']
        self.optimized_root = optimized_root




        # *********************************
        # making limited_supply_nodes
        # *********************************
        leaf_nodes_out       = self.leaf_nodes_out  # all leaf_nodes
        optimized_nodes_list = []              # leaf_node on targetted market
        limited_supply_nodes = []              # leaf_node Removed from target

        # 1. optimized_nodes辞書からキー項目をリストoptimized_nodes_listに抽出
        optimized_nodes_list = list(optimized_nodes.keys())

        # 2. leaf_nodes_outからoptimized_nodes_listの要素を排除して
        # limited_supply_nodesを生成
        limited_supply_nodes = [node for node in leaf_nodes_out if node not in optimized_nodes_list]

        # 結果を表示
        print("optimized_nodes_list:", optimized_nodes_list)
        print("limited_supply_nodes:", limited_supply_nodes)


# 最適化の結果をPSIに反映する方法
# 1. 入力ファイルS_month_data.csvをdataframeに読込み
# 2. limited_supply_nodesの各要素node nameに該当するS_month_dataのSの値を
#    すべて0 clearする。
# 3. 結果を"S_month_optimized.csv"として保存する
# 4. S_month_optimized.csvを入力として、load_data_opt_filesからPSI planする



        # limited_supply_nodesのリスト
        #limited_supply_nodes = ['MUC_N', 'MUC_D', 'MUC_I', 'SHA_I', 'NYC_D', 'NYC_I', 'LAX_D', 'LAX_I']

        # 入力CSVファイル名
        input_csv = 'S_month_data.csv'

        #input_csv_path = os.path.join(self.directory, input_csv)




        # デバッグ用コード追加
        print(f"self.directory: {self.directory}")
        print(f"input_csv: {input_csv}")

        if self.directory is None or input_csv is None:
            raise ValueError("self.directory または input_csv が None になっています。適切な値を設定してください。")

        input_csv_path = os.path.join(self.directory, input_csv)
        # 残りの処理







        # 出力CSVファイル名
        output_csv = 'S_month_optimized.csv'
        output_csv_path = os.path.join(self.directory, output_csv)




        # S_month.csvにoptimized_demandをセットする
        # optimized leaf_node以外を0 clearする

        # 関数を実行
        self.clear_s_values(limited_supply_nodes, input_csv_path, output_csv_path)



        ## **************************************
        ## input_csv = 'S_month_optimized.csv' load_files & planning
        ## **************************************
        #
        self.load_data_files4opt()     # loading with 'S_month_optimized.csv'

        #
        self.plan_through_engines4opt()




        # **************************************
        # いままでの評価と描画系
        # **************************************

        # *********************
        # evaluation
        # *********************
        self.update_evaluation_results4optimize()


        # *********************
        # network graph
        # *********************
        # STAY ORIGINAL PLAN
        # selfのhandle nameは、root_node_outboundで、root_node_out_optではない
        # 
        # グラフ描画関数を呼び出し  最適ルートを赤線で表示
        self.draw_network4opt(G, Gdm_structure, Gsp, pos_E2E, self.flowDict_opt)

        #self.draw_network4opt(G, Gdm, Gsp, pos_E2E, flowDict_dm, flowDict_sp, flowDict_opt)


        # *********************
        # PSI graph
        # *********************
        self.root.after(1000, self.show_psi_graph4opt)
        #self.root.after(1000, self.show_psi_graph)

        # パラメータの初期化と更新を呼び出し
        self.updated_parameters()
        #self.initialize_parameters()





    def reset_optimization_params(self, G):
        for u, v in G.edges():
            G[u][v]['capacity'] = 0
            G[u][v]['weight'] = 0
        for node in G.nodes():
            G.nodes[node]['demand'] = 0
    
    
    def reset_optimized_path(self, G):
        for u, v in G.edges():
            if 'flow' in G[u][v]:
                del G[u][v]['flow']
    
    
    def run_optimization(self, G):

        #flow_dict = nx.min_cost_flow(G)
        #cost = nx.cost_of_flow(G, flow_dict)
        #return flow_dict, cost


        # ************************************
        # optimize network
        # ************************************
        try:
    
            flowCost_opt, flowDict_opt = nx.network_simplex(G)

        except Exception as e:
            print("Error during optimization:", e)
            return

        self.flowCost_opt = flowCost_opt
        self.flowDict_opt = flowDict_opt

        print("flowDict_opt", flowDict_opt)
        print("flowCost_opt", flowCost_opt)

        print("end optimization")
    
    
    def add_optimized_path(self, G, flow_dict):
        for u in flow_dict:
            for v, flow in flow_dict[u].items():
                if flow > 0:
                    G[u][v]['flow'] = flow
    
    

    def show_error_message(self, message):
        # 画面にエラーメッセージを表示する関数
        import tkinter as tk
    
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        tk.Label(error_window, text=message, fg="red").pack()
        tk.Button(error_window, text="OK", command=error_window.destroy).pack()








    def copy_node(self, node_name):

        # オリジナルノードからコピーする処理

        original_node = self.nodes_outbound[node_name]  #オリジナルノードを取得
        copied_node = copy.deepcopy(original_node)  # deepcopyを使ってコピー
        return copied_node



    def create_optimized_tree(self, flowDict_opt):
        # Optimized Treeの生成
        optimized_nodes = {}
        for from_node, flows in flowDict_opt.items():

            if from_node == 'sales_office': # 末端の'sales_office'はtreeの外
                pass
            else:

                for to_node, flow in flows.items():

                    if to_node == 'sales_office': # 末端の'sales_office'はtreeの外
                        pass
                    else:


                        if flow > 0:
                            if from_node not in optimized_nodes:
                                optimized_nodes[from_node] = self.copy_node(from_node)
                            if to_node not in optimized_nodes:
                                optimized_nodes[to_node] = self.copy_node(to_node)
                                optimized_nodes[to_node].parent =optimized_nodes[from_node]
        return optimized_nodes




    def create_optimized_tree_OLD(self, flowDict_opt):

        # Optimized Treeの生成

        optimized_nodes = {}

        for from_node, flows in flowDict_opt.items():

            for to_node, flow in flows.items():

                if flow > 0:

                    if from_node not in optimized_nodes:
                        optimized_nodes[from_node] = self.copy_node(from_node)

                    if to_node not in optimized_nodes:
                        optimized_nodes[to_node] = self.copy_node(to_node)

                    optimized_nodes[to_node].parent =optimized_nodes[from_node]

        return optimized_nodes



    def set_optimized_demand(self, optimized_nodes, leaf_nodes, flowDict_opt):


        for node in self.nodes_outbound:
            self.nodes_outbound[node].psi4demand[:][0] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4demand[:][2] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4demand[:][3] = [] #週次S=[] clear

            self.nodes_outbound[node].psi4supply[:][0] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4supply[:][2] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4supply[:][3] = [] #週次S=[] clear

        for node in optimized_nodes:
            self.nodes_outbound[node].psi4demand[:][0] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4demand[:][2] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4demand[:][3] = [] #週次S=[] clear

            self.nodes_outbound[node].psi4supply[:][0] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4supply[:][2] = [] #週次S=[] clear
            self.nodes_outbound[node].psi4supply[:][3] = [] #週次S=[] clear


        # Optimized demandの設定
        for node in self.nodes_outbound:

            if node in optimized_nodes:

                if node in leaf_nodes:

            # leaf_nodeなので、これ flowDict_opt[node]で良い
            # 年間総量Sの値から、psi4demand[w][0]へmappingしなくてよい
            # original_nodeが持っている週次展開済みのS[w][0]をそのまま適用
            # 端数が出る販売チャネルに対しても、そのまま「満額回答」する

                    # Sのみイキ
                    #self.nodes_outbound[node].psi4demand[:][0] = [] #週次S=[] clear
                    self.nodes_outbound[node].psi4demand[:][2] = [] #週次S=[] clear
                    self.nodes_outbound[node].psi4demand[:][3] = [] #週次S=[] clear
            
                    self.nodes_outbound[node].psi4supply[:][0] = [] #週次S=[] clear
                    self.nodes_outbound[node].psi4supply[:][2] = [] #週次S=[] clear
                    self.nodes_outbound[node].psi4supply[:][3] = [] #週次S=[] clear


                # 最適化からはずれたnodeのweekly demandのみ0 ZERO clearする
                else:

                    optimized_nodes[node].psi4demand[:][0] = [] #週次S=[] clear
                    optimized_nodes[node].psi4demand[:][2] = [] #週次S=[] clear
                    optimized_nodes[node].psi4demand[:][3] = [] #週次S=[] clear

                    optimized_nodes[node].psi4supply[:][0] = [] #週次S=[] clear
                    optimized_nodes[node].psi4supply[:][2] = [] #週次S=[] clear
                    optimized_nodes[node].psi4supply[:][3] = [] #週次S=[] clear
                # optimized_nodes[node].S = flowDict_opt[node] if node in flowDict_opt else 0

            else:
                self.nodes_outbound[node].psi4demand[:][0] = [] #週次S=[] clear
                self.nodes_outbound[node].psi4demand[:][2] = [] #週次S=[] clear
                self.nodes_outbound[node].psi4demand[:][3] = [] #週次S=[] clear

                self.nodes_outbound[node].psi4supply[:][0] = [] #週次S=[] clear
                self.nodes_outbound[node].psi4supply[:][2] = [] #週次S=[] clear
                self.nodes_outbound[node].psi4supply[:][3] = [] #週次S=[] clear




# flowDict_opt = {'supply_point': {'DADEURO': 106, 'DADASIA': 180, 'DADAMER': 0}, 'DADEURO': {'HAM': 106}, 'HAM': {'HAM_N': 53, 'HAM_D': 53, 'HAM_I': 0, 'MUC': 0, 'FRALEAF': 0}, 'HAM_N': {'sales_office': 53}, 'HAM_D': {'sales_office': 53}, 'HAM_I': {'sales_office': 0}, 'MUC': {'MUC_N': 0, 'MUC_D': 0, 'MUC_I': 0}, 'MUC_N': {'sales_office': 0}, 'MUC_D': {'sales_office': 0}, 'MUC_I': {'sales_office': 0}, 'FRALEAF': {'sales_office': 0}, 'DADASIA': {'SHA': 17, 'CAN': 163}, 'SHA': {'SHA_N': 17, 'SHA_D': 0, 'SHA_I': 0}, 'SHA_N': {'sales_office': 17}, 'SHA_D': {'sales_office': 0}, 'SHA_I': {'sales_office': 0}, 'CAN': {'CAN_N': 53, 'CAN_D': 57, 'CAN_I': 53}, 'CAN_N': {'sales_office': 53}, 'CAN_D': {'sales_office': 57}, 'CAN_I': {'sales_office': 53}, 'DADAMER': {'NYC': 0, 'LAX': 0}, 'NYC': {'NYC_N': 0, 'NYC_D': 0, 'NYC_I': 0}, 'NYC_N': {'sales_office': 0}, 'NYC_D': {'sales_office': 0}, 'NYC_I': {'sales_office': 0}, 'LAX': {'LAX_N': 0, 'LAX_D': 0, 'LAX_I': 0}, 'LAX_N': {'sales_office': 0}, 'LAX_D': {'sales_office': 0}, 'LAX_I': {'sales_office': 0}, 'sales_office': {}}




    def set_optimization_params(self, G):
        print("optimization start")

        #Gdm = self.Gdm

        nodes_outbound = self.nodes_outbound
        root_node_outbound = self.root_node_outbound

        print("root_node_outbound.name", root_node_outbound.name)

        # Total Supply Planの取得
        total_supply_plan = int( self.total_supply_plan )

        #total_supply_plan = int(self.tsp_entry.get())


        print("setting capacity")
        max_capacity = 1000000  # 設定可能な最大キャパシティ（適切な値を設定）
        scale_factor_capacity = 1  # キャパシティをスケールするための因子
        scale_factor_demand   = 1  # スケーリング因子

        for edge in G.edges():
            from_node, to_node = edge

            # if node is leaf_node

            #@250103 STOP
            #if from_node in self.leaf_nodes_out and to_node == 'sales_office':

            #@250103 RUN
            if to_node in self.leaf_nodes_out:


                #@250103 RUN
                # ********************************************
                # scale_factor_capacity
                #@241220 TAX100... demand curve... Price_Up and Demand_Down
                # ********************************************
                capacity = int(nodes_outbound[to_node].nx_capacity * scale_factor_capacity)

                #@ STOP
                ## ********************************************
                ## scale_factor_capacity
                ##@241220 TAX100... demand curve... Price_Up and Demand_Down
                ## ********************************************
                #capacity = int(nodes_outbound[from_node].lot_counts_all * scale_factor_capacity)


                G.edges[edge]['capacity'] = capacity
            else:
                G.edges[edge]['capacity'] = max_capacity  # 最大キャパシティを設定
            print("G.edges[edge]['capacity']", edge, G.edges[edge]['capacity'])


        #@250102 MARK
        print("setting weight")
        for edge in G.edges():
            from_node, to_node = edge


            #@ RUN
            G.edges[edge]['weight'] = int(nodes_outbound[from_node].nx_weight)
            print("weight = nx_weight = cs_cost_total+TAX", nodes_outbound[from_node].name, int(nodes_outbound[from_node].nx_weight) )

            #@ STOP
            #G.edges[edge]['weight'] = int(nodes_outbound[from_node].cs_cost_total)
            #print("weight = cs_cost_total", nodes_outbound[from_node].name, int(nodes_outbound[from_node].cs_cost_total) )


        print("setting source and sink")

        # Total Supply Planの取得
        total_supply_plan = int( self.total_supply_plan )

        print("source:supply_point:-total_supply_plan", -total_supply_plan * scale_factor_demand)
        print("sink  :sales_office:total_supply_plan", total_supply_plan * scale_factor_demand)


        # scale = 1
        G.nodes['supply_point']['demand'] = -total_supply_plan * scale_factor_demand
        G.nodes['sales_office']['demand'] = total_supply_plan * scale_factor_demand


        print("optimizing supply chain network")

        for node in G.nodes():
            if node != 'supply_point' and node != 'sales_office':
                G.nodes[node]['demand'] = 0  # 他のノードのデマンドは0に設定



#        # ************************************
#        # optimize network
#        # ************************************
#        try:
#
#            flowCost_opt, flowDict_opt = nx.network_simplex(G)
#
#        except Exception as e:
#            print("Error during optimization:", e)
#            return
#
#        self.flowCost_opt = flowCost_opt
#        self.flowDict_opt = flowDict_opt
#
#        print("flowDict_opt", flowDict_opt)
#        print("flowCost_opt", flowCost_opt)
#
#        print("end optimization")




    def set_param_and_optimize_network(self, G):
        print("optimization start")

        #Gdm = self.Gdm

        nodes_outbound = self.nodes_outbound
        root_node_outbound = self.root_node_outbound

        print("root_node_outbound.name", root_node_outbound.name)

        # Total Supply Planの取得
        total_supply_plan = int( self.total_supply_plan )

        #total_supply_plan = int(self.tsp_entry.get())


        print("setting capacity")
        max_capacity = 1000000  # 設定可能な最大キャパシティ（適切な値を設定）
        scale_factor_capacity = 1  # キャパシティをスケールするための因子
        scale_factor_demand   = 1  # スケーリング因子

        for edge in G.edges():
            from_node, to_node = edge
            if from_node in self.leaf_nodes_out and to_node == 'sales_office':
                capacity = int(nodes_outbound[from_node].lot_counts_all * scale_factor_capacity)
                G.edges[edge]['capacity'] = capacity
            else:
                G.edges[edge]['capacity'] = max_capacity  # 最大キャパシティを設定

        print("setting weight")
        for edge in G.edges():
            from_node, to_node = edge
            G.edges[edge]['weight'] = int(nodes_outbound[from_node].cs_cost_total)
            print("weight = cs_cost_total", nodes_outbound[from_node].name, int(nodes_outbound[from_node].cs_cost_total) )


        print("setting source and sink")

        print("source:supply_point:", -total_supply_plan * scale_factor_demand)
        print("sink:sales_office:", total_supply_plan * scale_factor_demand)


        # scale = 1
        G.nodes['supply_point']['demand'] = -total_supply_plan * scale_factor_demand
        G.nodes['sales_office']['demand'] = total_supply_plan * scale_factor_demand


        print("optimizing supply chain network")

        for node in G.nodes():
            if node != 'supply_point' and node != 'sales_office':
                G.nodes[node]['demand'] = 0  # 他のノードのデマンドは0に設定


        # ************************************
        # optimize network
        # ************************************
        try:

            flowCost_opt, flowDict_opt = nx.network_simplex(G)

        except Exception as e:
            print("Error during optimization:", e)
            return

        self.flowCost_opt = flowCost_opt
        self.flowDict_opt = flowDict_opt

        print("flowDict_opt", flowDict_opt)
        print("flowCost_opt", flowCost_opt)

        print("end optimization")



if __name__ == "__main__":
    root = tk.Tk()

    app = PSIPlannerApp(root)
    print("PSIPlannerApp(root) is instanciated")

    #app4save = PSIPlannerApp4save(root)

    root.mainloop()

    root.destroy()


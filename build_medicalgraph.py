#!/usr/bin/env python3
# coding: utf-8
# File: MedicalGraph.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-3

import os
import json
import pandas as pd


class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/medical.json')
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="lhy",  # 数据库user name，如果没有更改过，应该是neo4j
            password="lhy123")

    '''读取文件'''
    def read_nodes(self):
        # 共７类节点
        drugs = [] # 药品
        foods = [] #　食物
        checks = [] # 检查
        departments = [] #科室
        producers = [] #药品大类
        diseases = [] #疾病
        symptoms = []#症状

        disease_infos = []#疾病信息

        # 构建节点实体关系
        rels_department = [] #　科室－科室关系
        rels_noteat = [] # 疾病－忌吃食物关系
        rels_doeat = [] # 疾病－宜吃食物关系
        rels_recommandeat = [] # 疾病－推荐吃食物关系
        rels_commonddrug = [] # 疾病－通用药品关系
        rels_recommanddrug = [] # 疾病－热门药品关系
        rels_check = [] # 疾病－检查关系
        rels_drug_producer = [] # 厂商－药物关系

        rels_symptom = [] #疾病症状关系
        rels_acompany = [] # 疾病并发关系
        rels_category = [] #　疾病与科室之间的关系


        count = 0
        for data in open(self.data_path):
            disease_dict = {}
            count += 1
            print(count)
            data_json = json.loads(data)
            disease = data_json['name']
            disease_dict['name'] = disease
            diseases.append(disease)
            disease_dict['desc'] = ''
            disease_dict['prevent'] = ''
            disease_dict['cause'] = ''
            disease_dict['easy_get'] = ''
            disease_dict['cure_department'] = ''
            disease_dict['cure_way'] = ''
            disease_dict['cure_lasttime'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''

            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])

            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany])

            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']

            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']

            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']

            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']

            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']

            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']
                if len(cure_department) == 1:
                     rels_category.append([disease, cure_department[0]])
                if len(cure_department) == 2:
                    big = cure_department[0]
                    small = cure_department[1]
                    rels_department.append([small, big])
                    rels_category.append([disease, small])

                disease_dict['cure_department'] = cure_department
                departments += cure_department

            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']

            if  'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']

            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']

            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']
                for drug in common_drug:
                    rels_commonddrug.append([disease, drug])
                drugs += common_drug

            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug])

            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                for _not in not_eat:
                    rels_noteat.append([disease, _not])

                foods += not_eat
                do_eat = data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease, _do])

                foods += do_eat
                recommand_eat = data_json['recommand_eat']

                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand])
                foods += recommand_eat

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check])
                checks += check
            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers += producer
            disease_infos.append(disease_dict)
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos,\
               rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,\
               rels_symptom, rels_acompany, rels_category

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    '''创建知识图谱中心疾病的节点'''
    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department']
                        ,cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob'])
            self.g.create(node)
            count += 1
            print(count)
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_diseases_nodes(disease_infos)
        self.create_node('Drug', Drugs)
        print(len(Drugs))
        self.create_node('Food', Foods)
        print(len(Foods))
        self.create_node('Check', Checks)
        print(len(Checks))
        self.create_node('Department', Departments)
        print(len(Departments))
        self.create_node('Producer', Producers)
        print(len(Producers))
        self.create_node('Symptom', Symptoms)
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('drug.txt', 'w+')
        f_food = open('food.txt', 'w+')
        f_check = open('check.txt', 'w+')
        f_department = open('department.txt', 'w+')
        f_producer = open('producer.txt', 'w+')
        f_symptom = open('symptoms.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return


class CVDKnowledgeGraphBuilder(MedicalGraph):
    """Class

    kg = CVDKnowledgeGraphBuilder()
    kg.export_csv()

    $ bin/neo4j-admin database import full cvd --nodes=import/node_disease.csv --nodes=import/node_check.csv --nodes=import/node_symptom.csv --nodes import/node_drug.csv --nodes import/node_food.csv --relationships=import/rel_check.csv --relationships import/rel_symptom.csv --relationships import/rel_drug.csv --relationships import/rel_doeat.csv --relationships import/rel_noteat.csv --relationships import/rel_recipe.csv
    """
    def __init__(self):
        self.data_path = os.path.join('data/medical.json')

    def filter_CVD(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        CVD_diseases = set([r[0] for r in rels_category if r[1] in ['心内科', '心胸外科']])
        CVD_diseases -= set([d for d in CVD_diseases if re.search('(胸|肺|肋|膈|食管|气管)', d)])

        # rels_commondrug_cvd = [tuple(r) for r in rels_commonddrug if r[0] in CVD_diseases]
        rels_drug_cvd = [tuple(r) for r in rels_recommanddrug if r[0] in CVD_diseases]
        CVD_Drugs = set(c[1] for c in rels_drug_cvd)

        rels_recommandeat_cvd = [tuple(r) for r in rels_recommandeat if r[0] in CVD_diseases]
        rels_doeat_cvd = [tuple(r) for r in rels_doeat if r[0] in CVD_diseases]
        rels_noteat_cvd = [tuple(r) for r in rels_noteat if r[0] in CVD_diseases]
        CVD_Foods = set([r[1] for r in rels_doeat_cvd + rels_noteat_cvd + rels_recommandeat_cvd])

        rels_check_cvd = [r for r in rels_check if r[0] in CVD_diseases]
        CVD_Checks = set(c[1] for c in rels_check_cvd)

        rels_symptom_cvd = [r for r in rels_symptom if r[0] in CVD_diseases]
        CVD_Symptoms = set(c[1] for c in rels_symptom_cvd)

        rels_acompany_cvd = [r for r in rels_acompany if r[0] in CVD_diseases]
        Related_diseases = set(c[1] for c in rels_acompany_cvd) - CVD_diseases

        return CVD_diseases, Related_diseases, CVD_Drugs, CVD_Foods, CVD_Checks, \
            CVD_Symptoms, rels_commondrug_cvd, rels_recommanddrug_cvd, \
            rels_recommandeat_cvd, rels_doeat_cvd, rels_noteat_cvd, \
            rels_check_cvd, rels_symptom_cvd, rels_acompany_cvd

    def export_csv2(self):
        """都改成 name"""
        CVD_diseases, Related_diseases, CVD_Drugs, CVD_Foods, CVD_Checks, \
            CVD_Symptoms, rels_commondrug_cvd, rels_recommanddrug_cvd, \
            rels_recommandeat_cvd, rels_doeat_cvd, rels_noteat_cvd, \
            rels_check_cvd, rels_symptom_cvd, rels_acompany_cvd = self.filter_CVD()

        df_disease = pd.DataFrame(
            {'name': list(CVD_diseases)+list(Related_diseases),
             ':LABEL': ['心血管及心脏疾病']*len(CVD_diseases) + \
             ['并发症']*len(Related_diseases)})
        df_disease.to_csv('node_disease.csv', index_label='diseaseId:ID(Disease-ID)')
        disease2index = df_disease.reset_index().set_index('name')['index']

        df_check = pd.DataFrame(list(CVD_Checks), columns=['name'])
        df_check[":LABEL"] = '检查'
        df_check.to_csv('node_check.csv', index_label='checkId:ID(Check-ID)')
        check2index = df_check.reset_index().set_index('name')['index']

        df_symptom = pd.DataFrame(list(CVD_Symptoms), columns=['name'])
        df_symptom[":LABEL"] = '症状'
        df_symptom.to_csv('node_symptom.csv', index_label='symptomId:ID(Symptom-ID)')
        symptom2index = df_symptom.reset_index().set_index('name')['index']

        df_drug = pd.DataFrame(list(CVD_Drugs), columns=['name'])
        df_drug[":LABEL"] = '药物'
        df_drug.to_csv('node_drug.csv', index_label='drugId:ID(Drug-ID)')
        drug2index = df_drug.reset_index().set_index('name')['index']

        df_food = pd.DataFrame(list(CVD_Foods), columns=['name'])
        df_food[":LABEL"] = '食物'
        df_food.to_csv('node_food.csv', index_label='foodId:ID(Food-ID)')
        food2index = df_food.reset_index().set_index('name')['index']

        df_rel_check = pd.DataFrame.from_records(
            rels_check_cvd, columns=['disease', 'check'])
        df_rel_check[':START_ID(Disease-ID)'] = df_rel_check['disease'].map(disease2index)
        df_rel_check[':END_ID(Check-ID)'] = df_rel_check['check'].map(check2index)
        df_rel_check[':TYPE'] = 'NEED_CHECK'
        df_rel_check.drop(['disease', 'check'], axis=1, inplace=True)
        df_rel_check.to_csv('rel_check.csv', index=False)

        df_rel_symptom = pd.DataFrame.from_records(
            rels_symptom_cvd, columns=['disease', 'symptom'])
        df_rel_symptom[':START_ID(Disease-ID)'] = df_rel_symptom['disease'].map(disease2index)
        df_rel_symptom[':END_ID(Symptom-ID)'] = df_rel_symptom['symptom'].map(symptom2index)
        df_rel_symptom[':TYPE'] = 'HAS_SYMPTOM'
        df_rel_symptom.drop(['disease', 'symptom'], axis=1, inplace=True)
        df_rel_symptom.to_csv('rel_symptom.csv', index=False)

        df_rel_drug = pd.DataFrame.from_records(
            rels_drug_cvd, columns=['disease', 'drug'])
        df_rel_drug[':START_ID(Disease-ID)'] = df_rel_drug['disease'].map(disease2index)
        df_rel_drug[':END_ID(Drug-ID)'] = df_rel_drug['drug'].map(drug2index)
        df_rel_drug[':TYPE'] = 'USE_DRUG'
        df_rel_drug.drop(['disease', 'drug'], axis=1, inplace=True)
        df_rel_drug.to_csv('rel_drug.csv', index=False)

        df_rel_doeat = pd.DataFrame.from_records(
            rels_doeat_cvd, columns=['disease', 'doeat'])
        df_rel_doeat[':START_ID(Disease-ID)'] = df_rel_doeat['disease'].map(disease2index)
        df_rel_doeat[':END_ID(Food-ID)'] = df_rel_doeat['doeat'].map(food2index)
        df_rel_doeat[':TYPE'] = 'CAN_EAT'
        df_rel_doeat.drop(['disease', 'doeat'], axis=1, inplace=True)
        df_rel_doeat.to_csv('rel_doeat.csv', index=False)

        df_rel_noteat = pd.DataFrame.from_records(
            rels_noteat_cvd, columns=['disease', 'noteat'])
        df_rel_noteat[':START_ID(Disease-ID)'] = df_rel_noteat['disease'].map(disease2index)
        df_rel_noteat[':END_ID(Food-ID)'] = df_rel_noteat['noteat'].map(food2index)
        df_rel_noteat[':TYPE'] = 'CANNOT_EAT'
        df_rel_noteat.drop(['disease', 'noteat'], axis=1, inplace=True)
        df_rel_noteat.to_csv('rel_noteat.csv', index=False)

        df_rel_recipe = pd.DataFrame.from_records(
            rels_recommandeat_cvd, columns=['disease', 'recipe'])
        df_rel_recipe[':START_ID(Disease-ID)'] = df_rel_recipe['disease'].map(disease2index)
        df_rel_recipe[':END_ID(Food-ID)'] = df_rel_recipe['recipe'].map(food2index)
        df_rel_recipe[':TYPE'] = 'RECOMMEND_EAT'
        df_rel_recipe.drop(['disease', 'recipe'], axis=1, inplace=True)
        df_rel_recipe.to_csv('rel_recipe.csv', index=False)

    def export_csv(self):
        CVD_diseases, Related_diseases, CVD_Drugs, CVD_Foods, CVD_Checks, \
            CVD_Symptoms, rels_commondrug_cvd, rels_recommanddrug_cvd, \
            rels_recommandeat_cvd, rels_doeat_cvd, rels_noteat_cvd, \
            rels_check_cvd, rels_symptom_cvd, rels_acompany_cvd = self.filter_CVD()

        df_disease = pd.DataFrame(
            {'Disease': list(CVD_diseases)+list(Related_diseases),
             ':LABEL': ['心血管及心脏疾病']*len(CVD_diseases) + \
             ['并发症']*len(Related_diseases)})
        df_disease.to_csv('node_disease.csv', index_label='diseaseId:ID(Disease-ID)')
        disease2index = df_disease.reset_index().set_index('Disease')['index']

        df_check = pd.DataFrame(list(CVD_Checks), columns=['Check'])
        df_check[":LABEL"] = '检查'
        df_check.to_csv('node_check.csv', index_label='checkId:ID(Check-ID)')
        check2index = df_check.reset_index().set_index('Check')['index']

        df_symptom = pd.DataFrame(list(CVD_Symptoms), columns=['Symptom'])
        df_symptom[":LABEL"] = '症状'
        df_symptom.to_csv('node_symptom.csv', index_label='symptomId:ID(Symptom-ID)')
        symptom2index = df_symptom.reset_index().set_index('Symptom')['index']

        df_drug = pd.DataFrame(list(CVD_Drugs), columns=['Drug'])
        df_drug[":LABEL"] = '药物'
        df_drug.to_csv('node_drug.csv', index_label='drugId:ID(Drug-ID)')
        drug2index = df_drug.reset_index().set_index('Drug')['index']

        df_food = pd.DataFrame(list(CVD_Foods), columns=['Food'])
        df_food[":LABEL"] = '食物'
        df_food.to_csv('node_food.csv', index_label='foodId:ID(Food-ID)')
        food2index = df_food.reset_index().set_index('Food')['index']

        df_rel_check = pd.DataFrame.from_records(
            rels_check_cvd, columns=['disease', 'check'])
        df_rel_check[':START_ID(Disease-ID)'] = df_rel_check['disease'].map(disease2index)
        df_rel_check[':END_ID(Check-ID)'] = df_rel_check['check'].map(check2index)
        df_rel_check[':TYPE'] = 'NEED_CHECK'
        df_rel_check.drop(['disease', 'check'], axis=1, inplace=True)
        df_rel_check.to_csv('rel_check.csv', index=False)

        df_rel_symptom = pd.DataFrame.from_records(
            rels_symptom_cvd, columns=['disease', 'symptom'])
        df_rel_symptom[':START_ID(Disease-ID)'] = df_rel_symptom['disease'].map(disease2index)
        df_rel_symptom[':END_ID(Symptom-ID)'] = df_rel_symptom['symptom'].map(symptom2index)
        df_rel_symptom[':TYPE'] = 'HAS_SYMPTOM'
        df_rel_symptom.drop(['disease', 'symptom'], axis=1, inplace=True)
        df_rel_symptom.to_csv('rel_symptom.csv', index=False)

        df_rel_drug = pd.DataFrame.from_records(
            rels_drug_cvd, columns=['disease', 'drug'])
        df_rel_drug[':START_ID(Disease-ID)'] = df_rel_drug['disease'].map(disease2index)
        df_rel_drug[':END_ID(Drug-ID)'] = df_rel_drug['drug'].map(drug2index)
        df_rel_drug[':TYPE'] = 'USE_DRUG'
        df_rel_drug.drop(['disease', 'drug'], axis=1, inplace=True)
        df_rel_drug.to_csv('rel_drug.csv', index=False)

        df_rel_doeat = pd.DataFrame.from_records(
            rels_doeat_cvd, columns=['disease', 'doeat'])
        df_rel_doeat[':START_ID(Disease-ID)'] = df_rel_doeat['disease'].map(disease2index)
        df_rel_doeat[':END_ID(Food-ID)'] = df_rel_doeat['doeat'].map(food2index)
        df_rel_doeat[':TYPE'] = 'CAN_EAT'
        df_rel_doeat.drop(['disease', 'doeat'], axis=1, inplace=True)
        df_rel_doeat.to_csv('rel_doeat.csv', index=False)

        df_rel_noteat = pd.DataFrame.from_records(
            rels_noteat_cvd, columns=['disease', 'noteat'])
        df_rel_noteat[':START_ID(Disease-ID)'] = df_rel_noteat['disease'].map(disease2index)
        df_rel_noteat[':END_ID(Food-ID)'] = df_rel_noteat['noteat'].map(food2index)
        df_rel_noteat[':TYPE'] = 'CANNOT_EAT'
        df_rel_noteat.drop(['disease', 'noteat'], axis=1, inplace=True)
        df_rel_noteat.to_csv('rel_noteat.csv', index=False)

        df_rel_recipe = pd.DataFrame.from_records(
            rels_recommandeat_cvd, columns=['disease', 'recipe'])
        df_rel_recipe[':START_ID(Disease-ID)'] = df_rel_recipe['disease'].map(disease2index)
        df_rel_recipe[':END_ID(Food-ID)'] = df_rel_recipe['recipe'].map(food2index)
        df_rel_recipe[':TYPE'] = 'RECOMMEND_EAT'
        df_rel_recipe.drop(['disease', 'recipe'], axis=1, inplace=True)
        df_rel_recipe.to_csv('rel_recipe.csv', index=False)


class KnowledgeGraphBuilder:
    """
    from neo4j import GraphDatabase, RoutingControl
    URI = "neo4j://localhost:7687"
    AUTH = ("neo4j", "12345678")
    """
    def __init__(self, driver):
        self.driver = driver

    def close(self):
        self.driver.close()

    def create_graph(self, diseases, drugs, associations):
        with self.driver.session() as session:
            # Create Disease nodes
            for disease in diseases:
                session.execute_write(self._create_disease_node, disease)

            # Create Drug nodes
            for drug in drugs:
                session.execute_write(self._create_drug_node, drug)

            # Create Disease-Drug relationships
            for association in associations:
                disease, drug = association
                session.execute_write(self._create_association, disease, drug)

    @staticmethod
    def _create_disease_node(tx, disease_name):
        tx.run("MERGE (d:Disease {name: $name})", name=disease_name)

    @staticmethod
    def _create_drug_node(tx, drug_name):
        tx.run("MERGE (d:Drug {name: $name})", name=drug_name)

    @staticmethod
    def _create_association(tx, disease_name, drug_name):
        tx.run("""
            MATCH (d:Disease {name: $disease_name})
            MATCH (dr:Drug {name: $drug_name})
            MERGE (d)-[:TREATS]->(dr)
        """, disease_name=disease_name, drug_name=drug_name)


if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:导入图谱节点中")
    handler.create_graphnodes()
    print("step2:导入图谱边中")
    handler.create_graphrels()


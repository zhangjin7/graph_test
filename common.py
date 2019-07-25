import configparser
from py2neo import Graph
from datasource import GreenPlum_Datasource
import re

class Neo4j_Graph:
    def __init__(self,path="conf/common.ini"):
        self.path=path
        self.conf = configparser.ConfigParser()
        self.conf.read(path,encoding="utf-8")
        self.graph = Graph(self.conf.get("graph","url"), auth=(self.conf.get("graph","user"), self.conf.get("graph","password")))

    @staticmethod
    def replace_param(param_list):
        new_param_list=[]
        for param in param_list:
            new_param=r'\"{'+param[1:]+r'}\"'
            new_param_list.append(new_param)
        return new_param_list

    @staticmethod
    def cypher_parser(cql):
        param_pattern=re.compile(r'\$\d{1,2}')
        # 替换'{','}' 为'{{','}}'
        cql=cql.replace('{','{{')
        cql=cql.replace('}','}}')
        # 替换参数 '$n' 为'\"{n}\"'
        param_list = param_pattern.findall(cql)
        new_param_list=Neo4j_Graph.replace_param(param_list)
        for i in range(len(param_list)):
            cql=cql.replace(param_list[i],new_param_list[i])
        cql=cql.split('|')
        position=cql[1]
        cql="\""+cql[0]+"\""
        # 解析sql字段对应的位置信息
        # position_list=position_pattern.findall(position)
        position_tuple=eval(position)
        format_str=".format("
        for i in position_tuple:
            format_str=format_str+"result["+str(i)+"],"
        format_str=format_str[:-1]+")"

        cql=cql+format_str
        return cql


        
    def add_data(self,data_type):
        ds = GreenPlum_Datasource(self.path)
        results=ds.get_data(data_type)
        conf_cql=self.conf.get("cypher",data_type)
        cql=Neo4j_Graph.cypher_parser(conf_cql)
        # print(cql)
        for result in results:
            eval("self.graph.run("+cql+")")
        ds.close()

    def infer_rel(self,infer_type):
        self.graph.run(self.conf.get("infer",infer_type))

if __name__=="__main__":
    g=Neo4j_Graph("conf/family_graph.ini")
    g.add_data("person")
    # g.infer_rel("relation")
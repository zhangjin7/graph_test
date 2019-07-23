import configparser
from py2neo import Graph,Node,Relationship,NodeMatcher,Subgraph
from person_rel_graph.datasource import GreenPlum_Datasource

class Neo_GraphDB:
    def __init__(self):
        self.graph=Graph("http://192.168.110.47:7474",auth=("neo4j","passwd"))
        self.conf=configparser.ConfigParser()
        self.conf.read("properties.conf",encoding="utf-8")

    @staticmethod
    def add_data(data_type):
        neo = Neo_GraphDB()
        ds =GreenPlum_Datasource()
        results = ds.get_data(data_type)
        results = ds.get_data(data_type)
        insert_stmt="neo.insert_"+data_type+"(results)"
        eval(insert_stmt)
        ds.close()

    def insert_person(self,results):
        nodes=[]
        for result in results:
            nodes.append(Node("Person",身份证号=result[0],姓名=result[1],性别=result[2],户籍号=result[3],户籍地址=result[4],户主身份证号=result[5],户主姓名=result[6]))
        tx=self.graph.begin()
        nodes=Subgraph(nodes)
        tx.merge(nodes,primary_key="身份证号",primary_label="Person")
        tx.commit()
    def insert_husband_rel(self,results):
        for result in results:
            self.graph.run("MATCH (p:Person),(q:Person) WHERE p.身份证号=\"%s\" AND q.身份证号=\"%s\" MERGE (p)-[r:丈夫]->(q)"%(result[3],result[0]))
    def insert_wife_rel(self,results):
        for result in results:
            self.graph.run("MATCH (p:Person),(q:Person) WHERE p.身份证号=\"%s\" AND q.身份证号=\"%s\" MERGE (p)-[r:妻子]->(q)"%(result[3],result[0]))
    def insert_father_rel(self,results):
        for result in results:
            self.graph.run("MATCH (p:Person),(q:Person) WHERE p.身份证号=\"%s\" AND q.身份证号=\"%s\" MERGE (p)-[r:父亲]->(q)"%(result[0],result[3]))
    def insert_mother_rel(self,results):
        for result in results:
            self.graph.run("MATCH (p:Person),(q:Person) WHERE p.身份证号=\"%s\" AND q.身份证号=\"%s\" MERGE (p)-[r:母亲]->(q)"%(result[0],result[3]))
    def insert_son_rel(self,results):
        for result in results:
            self.graph.run("MATCH (p:Person),(q:Person) WHERE p.身份证号=\"%s\" AND q.身份证号=\"%s\" MERGE (p)-[r:儿子]->(q)"%(result[3],result[0]))
    def insert_daughter_rel(self,results):
        for result in results:
            self.graph.run("MATCH (p:Person),(q:Person) WHERE p.身份证号=\"%s\" AND q.身份证号=\"%s\" MERGE (p)-[r:女儿]->(q)"%(result[3],result[0]))
    @staticmethod
    def infer_rel(infer_type):
        neo=Neo_GraphDB()
        neo.graph.run(neo.conf.get("infer",infer_type))

if __name__=="__main__":
    # 从数据库添加节点和关系用 add_data,从图数据库推断出关系用infer_rel方法
    Neo_GraphDB.add_data("daughter_rel")
    Neo_GraphDB.infer_rel("Relamarriage")
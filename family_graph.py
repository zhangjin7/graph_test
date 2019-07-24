import configparser
from py2neo import Graph,Node,Relationship,NodeMatcher,Subgraph
from datasource import GreenPlum_Datasource

class Family_Graph:
    def __init__(self,path="conf/family_graph.ini"):
        self.conf = configparser.ConfigParser()
        self.conf.read(path,encoding="utf-8")
        self.graph = Graph(self.conf.get("family_graph","url"), auth=(self.conf.get("family_graph","user"), self.conf.get("family_graph","password")))

    @staticmethod
    def add_node(data_type,path="conf/family_graph.ini"):
        neo = Family_Graph(path)
        ds =GreenPlum_Datasource(path)
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

    @staticmethod
    def add_relation(data_type,path="conf/family_graph.ini"):
        neo = Family_Graph(path)
        ds = GreenPlum_Datasource(path)
        results=ds.get_data(data_type)
        #cypher
        cql_parser=neo.conf.get("cql",data_type).split("$")
        cql=cql_parser[0]
        position=cql_parser[1]
        for result in results:
            # neo.graph.run("MATCH (p:Person),(q:Person) WHERE p.电话号码={0} AND q.电话号码={1} MERGE (p)-[r:通话]->(q)".format(result[0],result[1]))
            eval("neo.graph.run(\""+cql+"\".format("+position+"))")
        ds.close()

    @staticmethod
    def infer_rel(infer_type,path="conf/family_graph.ini"):
        neo=Family_Graph(path)
        neo.graph.run(neo.conf.get("infer",infer_type))

if __name__=="__main__":
    # 从数据库添加节点add_node("节点名"),添加关系用add_relation("关系名"),从图数据库推断出关系用infer_rel("关系名")方法
    # Family_Graph.add_node("person")
    Family_Graph.add_relation("husband_rel")
    # Family_Graph.infer_rel("relatives_by_marriage")
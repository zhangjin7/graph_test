import configparser
from py2neo import Graph,Node,Subgraph
from datasource import GreenPlum_Datasource

class Event_Graph:
    def __init__(self,path="conf/event_graph"):
        self.conf = configparser.ConfigParser()
        self.conf.read(path,encoding="utf-8")
        self.graph = Graph(self.conf.get("event_graph","url"), auth=(self.conf.get("event_graph","user"), self.conf.get("event_graph","password")))

    @staticmethod
    def add_node(data_type,path="conf/event_graph.ini"):
        neo = Event_Graph(path)
        ds =GreenPlum_Datasource(path)
        results = ds.get_data(data_type)
        insert_stmt="neo.insert_"+data_type+"(results)"
        eval(insert_stmt)
        ds.close()

    def insert_person(self,results):
        nodes=[]
        for result in results:
            nodes.append(Node("Person",姓名=result[0],身份证号=result[1],性别=result[2],电话号码=result[3]))
        tx=self.graph.begin()
        nodes=Subgraph(nodes)
        tx.merge(nodes,primary_key="身份证号",primary_label="Person")
        tx.commit()

    @staticmethod
    def add_data(data_type,path="conf/event_graph.ini"):
        neo = Event_Graph(path)
        ds = GreenPlum_Datasource(path)
        results=ds.get_data(data_type)
        #cypher
        cql_parser=neo.conf.get("cql",data_type).split("$")
        cql=cql_parser[0]
        position=cql_parser[1]
        for result in results:
            # print(r"MERGE (n:Person {{身份证号: \"{1}\"}}) on create set n.姓名=\"{0}\",n.身份证号=\"{1}\",n.性别=\"{2}\",n.电话号码=\"{3}\"".format(
            #         result[0], result[1], result[2], result[3]))
            eval("neo.graph.run(\""+cql+"\".format("+position+"))")
        ds.close()

if __name__=="__main__":
    # 添加节点add_node("节点名"),通过配置的sql和cql添加用add_data("数据类型")
    Event_Graph.add_data("person")
    # Event_Graph.add_node("person")



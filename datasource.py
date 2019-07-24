import psycopg2
import configparser

#greenplum或者postgresql
class GreenPlum_Datasource:
    def __init__(self,path):
        self.conf=configparser.ConfigParser()
        self.conf.read(path,encoding="utf-8")
        self.host=self.conf.get("datasource","host")
        self.port=self.conf.get("datasource","port")
        self.user=self.conf.get("datasource","user")
        self.passwd=self.conf.get("datasource","passwd")
        self.database=self.conf.get("datasource","database")
        self.conn=psycopg2.connect(host=self.host,port=self.port,database=self.database,user=self.user,password=self.passwd)
        self.cursor=self.conn.cursor()
        print(self.host+":"+self.port+"\\"+self.database)

    def get_data(self,data_type):
        sql=self.conf.get("sql",data_type)
        self.cursor.execute(sql)
        result=self.cursor.fetchall()
        return result

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__=="__main__":
    ds=GreenPlum_Datasource("conf/family_graph.ini")
    result=ds.get_data("daughter_rel")
    print(result)
    ds.close()



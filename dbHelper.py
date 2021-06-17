import mysql.connector #mysql.connector MySQL veri tabanına 
#erişmek için kullanılan birMySQL sürücüsüdür.

class dBHelper:
    def __init__(self):# dBHelper sınıfı yapıcı metodu
        self.connection = mysql.connector.connect(# mysql.connector kütüphanesinin connect isimli fonksiyonu  
            #veritabanın bilgilerini parametre olarak alır ve veritabanı bağlantısını gerçekleştirir.
            host="localhost",#Projenin kullanıldığı sunucu bilgisayarı(yerel bilgisayar).
            user="root",# Veri tabanı kullanıcı adı
            database="veritabani_zorunlu_proje_son",# Projede  kullanılan veritabanının adı.
            auth_plugin='mysql_native_password'# Kimlik doğrulama eklentisi.
        )
        self.cursor = self.connection.cursor(dictionary=True)# cursor objesi oluşturulur ve verilerin sözlük 
                                                                # şeklinde gelmesini sağlamak için parametre verilmiştir



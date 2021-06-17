from flask import Flask, url_for, render_template, redirect, request, session, flash
from flask.helpers import flash
import dbHelper
import datetime
from werkzeug.datastructures import ImmutableMultiDict

db = dbHelper.dBHelper()
cursor = db.cursor
app = Flask(__name__)
app.secret_key = "AAAAAAAAAAAAAAAAA"

# SON HALI 16.06.2021 - 21:32

@app.route('/')
def home():
    return redirect(url_for('login'))

# UYE KAYIT ETME FONKSİYONU- bitti
# /register url'ine GET ve POST istekleri atılabilir.
@app.route('/register', methods=['POST', 'GET'])
def register():
    if "username" in session: # Oturum kontrolü
        error = ''
        if request.method == 'POST': # İstek methodu kontrolü
            imd = ImmutableMultiDict(request.form) # Formdan gelen verileri ImmutableMultiDict formatına dönüştürür.
            üyeBilgi = imd.to_dict(flat=False)
            uyelerData = uyeSorgu() # Veritabanında bulunan bütün üyeleri ve bilgilerini getiren fonksiyonu çağırır.
            uyelerData = [i['Eposta'] for i in uyelerData] # Gelen üyelerin eposta bilgileri 'uyelerData' listesinde tutulur.
            if request.form['ad'] == '': # Form içinde Ad inputu kontrolü
                error = 'Ad girin'
            elif request.form['soyad'] == '': # Form içindeki Soyad inputu kontrolü
                error = 'Soyad girin'
            elif request.form['telefon'] == '': # Form içindeki telefon inputu kontrolü
                error = 'Telefon girin'
            elif request.form['il'] == '0': # Form içindeki il inputu kontrolü
                error = 'İl ve İlçe girin'
            elif not 'ilce' in üyeBilgi: # Form içindeki ilce inputu kontrolü
                error = 'İl ve ilçe girin'
            elif request.form['ilce'] == '0': # Form içindeki ilce inputu kontrolü
                error = 'İlçe girin'
            elif request.form['postakodu'] == '': # Form içindeki postakodu inputu kontrolü
                error = 'Postakodu girin'
            elif request.form['ikamet'] == '': # Form içindeki ikamet inputu kontrolü
                error = 'İkamet adresi girin'
            elif request.form['email'] == '': # Form içindeki email inputu kontrolü
                error = 'E-maili girin'
            else:
                if üyeBilgi['email'][0] in uyelerData: # Kayıt olmaya çalışan üyenin eposta bilgisi veritabanında mevcut mu kontrolü
                    error = 'Üye zaten mevcut'
                    return render_template('register.html', error=error) # Varsa aynı sayfaya hata mesajı döndürülür. Yoksa aşağıdaki satırlar çalışır.
                sql = f"""insert into adresler (Il, Ilce, PostaKodu, İkamet_Adresi)
                values
                ('{üyeBilgi['il'][0]}',
                '{üyeBilgi['ilce'][0]}',
                '{üyeBilgi['postakodu'][0]}',
                '{üyeBilgi['ikamet'][0]}')
                """
                # Adresler tablosuna formlardan gelen veriler ile üyenin il, ilçe, postakodu ve ikamet adresi bilgisi kaydedilir.
                cursor.execute(sql) # SQL sorgusunun çalıştırılmasını sağlar.
                db.connection.commit() # Veritabanında yapılan değişiklikleri commit eder yani kaydeder.
                sql2 = f"""insert into uyeler (Ad, Soyad, Eposta, Telefon, AdresID) values
                ('{üyeBilgi['ad'][0]}',
                '{üyeBilgi['soyad'][0]}',
                '{üyeBilgi['email'][0].lower()}',
                '{üyeBilgi['telefon'][0]}',
                {cursor.lastrowid})"""
                # Uyeler tablosuna üyenin ad, soyad, email ve telefon bilgisi kaydedilir.
                # Tabloya girilen son verinin ID bilgisini getirir.
                #  Bunu yapma sebebimiz Üyeler tablosunun bir adresID bilgisine ihtiyaç duymasıdır.
                cursor.execute(sql2) # SQL sorgusunun çalıştırılmasını sağlar.
                db.connection.commit() # Veritabanında yapılan değişiklikleri commit eder yani kaydeder. 
                return redirect(url_for('register')) # İşlem gerçekleştikten sonra aynı sayfaya yönlendirir.
        return render_template('register.html', error=error) # Sayfa yüklendiğinde register.html dosyası ekrana basılır.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.

# ADMIN GİRİŞ YAPMA FONKSİYONU-biti
# /login url'ine GET ve POST istekleri atılabilir.
@app.route('/login', methods=["GET", "POST"])
def login(): # /login url'inde çalışacak fonksiyon
    if "username" not in session: # Oturum kontrolü
        error = ''
        if request.method == 'POST': # İstek methodu kontrolü
            username = request.form['username'] # Formdan gelen username inputu
            password = request.form['password'] # Formdan gelen password inputu
            sql = f"""SELECT * FROM adminler where '{username}' = KullaniciAdi and Sifre = '{password}' """
            # adminler tablosunun KullaniciAdi sütunu inputtan gelen username verisine eşitse
            # ve adminler tablosunun Sifre sütunu inputtan gelen uyetelefon verisine eşitse
            # sorgunun sağlandığı bütün satırları getirir.
            cursor.execute(sql) # SQL sorgusunun çalıştırılmasını sağlar.
            data = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
            if data: # Veri mevcut mu kontrolü yapılır.
                session['username'] = username # Mevcutsa kullanıcı adı (username) session'a kaydedilir.
                adminId() # Adminin hangi kütüphaneden sorumlu olduğunu session'a kaydeden fonksiyon
                return redirect(url_for('home')) # Anasayfaya yönlendirir.
            else: # Veri mevcut değilse
                error = 'Girdiğiniz e-posta veya cep telefonu numarası bir hesaba ait değil.' # Ekrana basılacak hata mesajı
        return render_template('login.html', error=error) # Hata mesajını HTML sayfasına gönderir
    else:# Oturum zaten açıksa ana ekrana yönlendirir.
        return redirect(url_for('search')) 

# ÜYE GORUNTULEME İÇİN UYE GİRİŞ EKRANI -bitti
# /member url'ine GET ve POST istekleri atılabilir.
@app.route('/member', methods=["GET", "POST"])
def member():
    # /member url'inde çalışacak fonksiyon
    error = '' # Hataları depolamak için error değişkeni tanımladık
    if request.method == 'POST': # İstek metodu kontrolü
        uyemail = request.form['memberemail'] # Formdan gelen email inputu
        uyetelefon = request.form['membertel'] # Formdan gelen telefon inputu
        sql = f"""SELECT * FROM uyeler where '{uyemail}' = Eposta and Telefon = '{uyetelefon}' """
        # uyeler tablosunun Eposta sütunu inputtan gelen uyeemail verisine eşitse
        # ve uyeler tablosunun Telefon sütunu inputtan gelen uyetelefon verisine eşitse
        # sorgunun sağlandığı bütün satırları getirir.

        cursor.execute(sql) # SQL sorgusunun çalıştırılmasını sağlar.
        data = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
        # veritabanından çekilmesini sağlar.

        if data: # Veri mevcut mu kontrolü yapılır
            return redirect(url_for('profile', email=uyemail)) # Veritabanından gelen veriyle profil sayfasına yonlendirilir.
        else: # Veri mevcut değilse 
            error = 'Girdiğiniz e-posta veya cep telefonu numarası bir hesaba ait değil.' #Hata mesajını ekranda göstermek için yukarda tanımlanan değişkene atama yapılır
    return render_template('memberlogin.html', error=error) # Hata mesajı HTML sayfasına gönderilir.
    

# ÇIKIS FONKSİYONU -bitti
# /logout url'ine GET ve POST istekleri atılabilir.
@app.route('/logout')
def logout():
    # /login url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        del session['username'] # Session'dan username bilgisi siliniyor.
    return redirect(url_for('login')) # Login sayfasına yönlendirilir.

# UYE PROFİL KISMI -bitti
# /profile/<email> url'ine GET ve POST istekleri atılabilir.
@app.route('/profile/<email>', methods=["GET", "POST"])
def profile(email):
    # /profile/<email> url'inde çalışacak fonksiyon
    sql8 = f"""SELECT ad, soyad, eposta, telefon, il, ilce, İkamet_Adresi  FROM uyeler 
    left JOIN adresler on adresler.ID = uyeler.AdresID
    where eposta = '{email}'"""
    # uyeler tablosu ile adresler tablosu Adres ID'ler üzerinden birleştirilir.
    # Birleşmiş tablodan uyeler tablosunun Eposta sütunu url argümanı olarak gelen email verisine eşitse
    # sorgunun sağlandığı bütün satırları getirir.


    cursor.execute(sql8) # SQL sorgusunun çalıştırılmasını sağlar.
    uyeData = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
    # veritabanından çekilmesini sağlar.


    sqlUyeID = f"""select ID from uyeler where Eposta='{email}';"""
    # uyeler tablosunun Eposta sütunu inputtan gelen uyeemail verisine eşitse
    # ve uyeler tablosunun Eposta sütunu url argümanı olarak gelen email verisine eşitse
    # sorgunun sağlandığı satırların sadece ID sütununu getirir.

    cursor.execute(sqlUyeID) # SQL sorgusunun çalıştırılmasını sağlar.
    uyeID = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
    # veritabanından çekilmesini sağlar.
    uyeID = uyeID[0]['ID'] # uyeID veritabanından gelen veridir ve bu verinin içinden 
    #sadece ID sütunun verisi alınır ve uyeID değişkenine atılır

    sqlDurum0Kitaplar = f"""SELECT Baslik,AlimTarih FROM kitap_emanet left join kitaplar on 
    kitap_emanet.ISBN=kitaplar.ISBN
    where kitap_emanet.UyeID={uyeID} and kitap_emanet.Durum=0;"""
    # kitap_emanet tablosu ile kitaplar tablosu ISBN'ler üzerinden birleştirilir.
    # Birleşmiş tablodan kitap_emanet tablosunun uyeID sütunu yukarda tanımlanan uyeID değişkenine eşitse 
    # ve kitap_emanet tablosunun Durum değerini 0'a(0 değeri teslim edilmemiş kitapları temsil eder) eşitse
    # sorgunun sağlandığı  satırların Baslik,AlimTarih sütunları getirilir.
    cursor.execute(sqlDurum0Kitaplar) # SQL sorgusunun çalıştırılmasını sağlar.
    durum0 = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
    # veritabanından çekilmesini sağlar.
    

    sqlDurum1Kitaplar = f"""SELECT Baslik,TeslimTarih FROM kitap_emanet left join kitaplar on 
    kitap_emanet.ISBN=kitaplar.ISBN
    where kitap_emanet.UyeID={uyeID} and kitap_emanet.Durum=1;"""
    # kitap_emanet tablosu ile kitaplar tablosu ISBN'ler üzerinden birleştirilir.
    # Birleşmiş tablodan kitap_emanet tablosunun uyeID sütunu yukarda tanımlanan uyeID değişkenine eşitse 
    # ve kitap_emanet tablosunun Durum değerini 1'e(1 değeri teslim edilmiş kitapları temsil eder) eşitse
    # sorgunun sağlandığı  satırların Baslik,TeslimTarih sütunları getirilir.
    cursor.execute(sqlDurum1Kitaplar) # SQL sorgusunun çalıştırılmasını sağlar.
    durum1 = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
    # veritabanından çekilmesini sağlar.
    
    
    return render_template('profile.html', uyeData=uyeData[0], durum0=durum0, durum1=durum1) # uyeData ile uyebilgilerini, 
    # durum0 ile teslim edilmemiş kitap bilgilerini, durum1 ile teslim edilmiş kitap bilgilerini profile.html'e  gönderir.
    # Bu veriler HTML sayfasında gerekli yerlere yazılır
    

# /profile/<email> url'ine GET ve POST istekleri atılabilir.
@app.route('/profile-edit', methods=["GET", "POST"])
def profile_edit():
    email = request.args.get('edit')
    
    error = '' # Hataları depolamak için error değişkeni tanımladık
    if request.method == 'POST': # İstek metodu kontrolü
        
        imd = ImmutableMultiDict(request.form) # Formdan gelen verileri ImmutableMultiDict formatına dönüştürür.
        üyeBilgi = imd.to_dict(flat=False)
        uyelerData = uyeSorgu() # Veritabanında bulunan bütün üyeleri ve bilgilerini getiren fonksiyonu çağırır.
        uyelerData = [i['Eposta'] for i in uyelerData] # Gelen üyelerin eposta bilgileri 'uyelerData' listesinde tutulur.
        if request.form['ad'] == '': # Form içinde Ad inputu kontrolü
            error = 'Ad girin'
        elif request.form['soyad'] == '': # Form içindeki Soyad inputu kontrolü
            error = 'Soyad girin'
            
        elif request.form['telefon'] == '': # Form içindeki telefon inputu kontrolü
            error = 'Telefon girin'
            
        elif request.form['il'] == '0': # Form içindeki il inputu kontrolü
            error = 'İl ve İlçe girin'
            
        elif not 'ilce' in üyeBilgi: # Form içindeki ilce inputu kontrolü
            error = 'İl ve ilçe girin'
            
        elif request.form['ilce'] == '0': # Form içindeki ilce inputu kontrolü
            error = 'İlçe girin'
        elif request.form['postakodu'] == '': # Form içindeki postakodu inputu kontrolü
            error = 'Postakodu girin'
        elif request.form['ikamet'] == '': # Form içindeki ikamet inputu kontrolü
            error = 'İkamet adresi girin'
        elif request.form['email'] == '': # Form içindeki email inputu kontrolü
            error = 'E-maili girin'
        else: # Boş bırakılmamışssa
            
            sqlUyeID = f"""select ID,Ad,Soyad,Telefon,Eposta,AdresID from uyeler where Eposta='{email}';"""
            # uyeler tablosunun Eposta sütunu argüman olarak gelen emaile eşitse
            # sorgunun sağlandığı satırların sadece ID sütununu getirir.

            cursor.execute(sqlUyeID) # SQL sorgusunun çalıştırılmasını sağlar.
            uyeID = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            
            yeniEposta = request.form['email'] # Forma girilen yeni eposta adresi
            butunUyeler = uyeSorgu() # bütün üyelerin bilgilerini geçen fonksiyon
            
            butunUyelerEposta = butunUyeler[0]['Eposta'] # bütün üyelerin bilgileri arasından sadece epostalarını bir listede tutuyoruz.
            
            if yeniEposta in butunUyelerEposta: # Eğer yeni eposta daha önceden tanımlı bir e posta ise
                if yeniEposta!=uyeID[0]['Eposta']: # ve yeni e posta önceki eposta değilse
                    #yani örneğin kullanıcı emailini değilde sadece adresini değiştirdiyse hata vermesini önlemek için kullanılan kontrol.
                    flash('Yeni girilen Eposta başkası tarafından kullanılıyor', 'danger') 
                    # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return redirect(url_for('member')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.


            sqlEditUye=f""" UPDATE uyeler SET ad='{request.form['ad']}',soyad='{request.form['soyad']}',Eposta='{request.form['email']}',
            Telefon='{request.form['telefon']}' where uyeler.ID={uyeID[0]['ID']}; """
            cursor.execute(sqlEditUye) # SQL sorgusunun çalıştırılmasını sağlar.
            db.connection.commit()
            # uyeler tablosunun uyeId'si argüman olarak gelen emailin sahibinin idsine eşitse 
            # o satırdaki üyeyi yeni formdan gelen verilerle güncelleyen sorgu


            sqlEditAdres=f""" UPDATE adresler SET Il='{request.form['il']}',Ilce='{request.form['ilce']}',İkamet_Adresi='{request.form['ikamet']}',
            PostaKodu='{request.form['postakodu']}' where adresler.ID={uyeID[0]['AdresID']}; """
            cursor.execute(sqlEditAdres) # SQL sorgusunun çalıştırılmasını sağlar.
            db.connection.commit()
            # uyeler tablosunun adresID'si argüman olarak gelen emailin sahibinin adresID eşitse 
            # o satırdaki adres bilgilerini yeni formdan adres gelen verileriyle güncelleyen sorgu
            flash('Kullanıcı bilgileri başarıyla güncellendi ', 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
            return redirect(url_for('member')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
    else:
        # get methodu ile bu sayfaya yönlendirilirse çalışacak kısım.
        # güncellenecek insanın üstünde değişiklik yapabilsin diye eski verilerini getiren kısım.
        
        sql8 = f"""SELECT uyeler.id,ad, soyad, eposta, telefon, il, ilce, İkamet_Adresi,adresler.postakodu  FROM uyeler 
        left JOIN adresler on adresler.ID = uyeler.AdresID
        where eposta = '{email}'"""
        # uyeler tablosu ile adresler tablosu Adres ID'ler üzerinden birleştirilir.
        # Birleşmiş tablodan uyeler tablosunun Eposta sütunu url argümanı olarak gelen email verisine eşitse
        # sorgunun sağlandığı bütün satırları getirir.


        cursor.execute(sql8) # SQL sorgusunun çalıştırılmasını sağlar.
        uyeData = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
        # veritabanından çekilmesini sağlar.

        return render_template('uyeDuzenle.html', uyeData=uyeData[0]) # uyeData ile uyebilgilerini, 
        # durum0 ile teslim edilmemiş kitap bilgilerini, durum1 ile teslim edilmiş kitap bilgilerini uyeDuzenle.html'e  gönderir.
        # Bu veriler HTML sayfasında gerekli yerlere yazılır
    flash('Bütün alanları doldurun', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
    return redirect(url_for('member')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.



# KENDI KUTUPHANENDE ARAMA YAPMA- bitti
# /search/ url'ine GET ve POST istekleri atılabilir.
@app.route('/search/', methods=["GET", "POST"])
def search():
    # /search/ url'inde çalışacak fonksiyon
    if "username" in session:
        # Oturum kontrolü
        select = request.args.get('select') # Formdan gelen arama kriteri inputu
        inputData = request.args.get('data') # Formdan gelen aranacak veri bilgisi

        if select == 'KITAPLAR.ISBN': # Arama kriteri ISBN seçilmişse
            sql = f"""
            select * from kitap_kutuphane 
	        join kitaplar on kitaplar.ISBN = kitap_kutuphane.ISBN
	        where kitap_kutuphane.ISBN = "{inputData}" and kitap_kutuphane.KutuphaneID={session['kutuphane']};
            """
            # Kitap_kutuphane tablosu ile kitaplar tablosu ISBN'ler üzerinden birleştirilir.
            # Birleşmiş tablodan kitap_kutuphane tablosunun ISBN sütunu inputtan gelen ISBN verisine eşitse
            # ve kitap_kutuphane tablosunun KutuphaneID sütunu Adminin sorumlu olduğu kütüphanenin ID'sine eşitse
            # sorgunun sağlandığı bütün satırları getirir.

            cursor.execute(sql)# SQL sorgusunun çalıştırılmasını sağlar.
            
            data = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.


            if(not data): # Veri mevcut değilse
                return render_template('search.html') # Aynı sayfada herhangi bir veri gösterilmez
            sqlYazalar = f"""
            select CONCAT(yazarlar.Ad, ' ', yazarlar.Soyad) AS tamAd from kitap_yazar 
	        join yazarlar on yazarlar.ID = kitap_yazar.YazarID
            where kitap_yazar.ISBN = "{inputData}";
            """
            # kitap_yazar tablosu ile yazarlar tablosu Yazar ID'leri üzerinden birleştirilir.
            # Birleşmiş tablodan kitap_yazar tablosunun ISBN sütunu inputtan gelen ISBN verisine eşitse
            # sorgunun sağlandığı satırların sadece yazarlar.Ad ve yazarlar.Soyad sütunları
            # tamAd olarak birleştirilerk getirir.
            cursor.execute(sqlYazalar) # SQL sorgusunun çalıştırılmasını sağlar.
            yazarList = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            yazar = [i['tamAd'] for i in yazarList] # Veritabanından gelen veri 'yazar' adlı liste değişkeninde tutulur.
            data[0]['yazarlarinTamami'] = yazar # 'Yazar' listesi data[0]a 'yazarlarinTamami' anahtar bilgisi ile atanır.
        
            sqlKategoriler = f"""
            select Ad from kitap_kategori
	        join kategoriler on kategoriler.id = kitap_kategori.KategoriID
            where kitap_kategori.ISBN = "{inputData}";
            """
            # kitap_kategori tablosu ile kategoriler tablosu Kategori ID'leri üzerinden birleştirilir.
            # Birleşmiş tablodan kitap_kategori tablosunun ISBN sütunu inputtan gelen ISBN verisine eşitse
            # sorgunun sağlandığı satırların sadece Ad (KATEGORİ ADI) sütunu getirilir.
            cursor.execute(sqlKategoriler) # SQL sorgusunun çalıştırılmasını sağlar.
            kategorilerList = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            kategori = [i['Ad'] for i in kategorilerList] # Veritabanından gelen veri 'kategori' adlı liste değişkeninde tutulur.
            data[0]['kategorilerinTamami'] = kategori # 'kategori' listesi data[0]a 'kategorilerinTamami' anahtar bilgisi ile atanır.
        

            sqlKutuphaneAdi = f"""
            select Ad from kutuphaneler where ID = {session['kutuphane']};
            """
            # kutuphaneler tablosundan ID sütunu Adminin sorumlu olduğu kütüphanenin ID sine eşitse 
            # sorguya uyan satırın Ad sütununu getirir.
            cursor.execute(sqlKutuphaneAdi)# SQL sorgusunun çalıştırılmasını sağlar.
            kutuphaneAdi = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            kutuphane = [i['Ad'] for i in kutuphaneAdi] # Veritabanından gelen veri 'kutuphane' adlı liste değişkeninde tutulur.
            data[0]['kutuphaneAdi'] = kutuphane # 'kutuphane' listesi data[0]a 'kutuphaneAdi' anahtar bilgisi ile atanır.
            return render_template('search.html', data=data) # Bu data listesi gösterilmek üzere bulunulan sayfaya gönderilir.
            # HTML içeriğinde gerekli alanlarda gösterilir.
        elif select == 'Baslik': # Arama kriteri Baslik seçilmişse
            sqlBasliklar = f"""
            SELECT ISBN from kitaplar where baslik LIKE '%{inputData}%';
            """
            # kitaplar tablosunda baslik sütunu verileri gelen input verisini içeriyorsa 
            # şartı sağlayan verilerin ISBN sütunu getirilir.
            cursor.execute(sqlBasliklar)# SQL sorgusunun çalıştırılmasını sağlar.
            isbnler = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            data = []
            datalar = []
            for i in range(len(isbnler)): # Sorgu sonuçlarını içeren listenin 
                #uzunluğu kadar for döngüsü oluşturulur.

                isbn = isbnler[i]['ISBN'] # Geçerli indisin ISBN verisi isbn değişkeninde tutulur.
                sql = f"""
                select * from kitap_kutuphane 
                join kitaplar on kitaplar.ISBN = kitap_kutuphane.ISBN
                where kitap_kutuphane.ISBN = "{isbn}" and kitap_kutuphane.KutuphaneID={session['kutuphane']};
                """
                # Kitap_kutuphane tablosu ile kitaplar tablosu ISBN'ler üzerinden birleştirilir.
                # Birleşmiş tablodan kitap_kutuphane tablosunun ISBN sütunu isbn değişkenine eşitse
                # ve kitap_kutuphane tablosunun KutuphaneID sütunu Adminin sorumlu olduğu kütüphanenin ID'sine eşitse
                # sorgunun sağlandığı bütün satırları getirir.
                cursor.execute(sql)# SQL sorgusunun çalıştırılmasını sağlar.
                data = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
                # veritabanından çekilmesini sağlar.
                if(not data): # Veri yoksa döngü bir ilerletilir.
                    continue
                sqlYazalar = f"""
                select CONCAT(yazarlar.Ad, ' ', yazarlar.Soyad) AS tamAd from kitap_yazar 
                join yazarlar on yazarlar.ID = kitap_yazar.YazarID
                where kitap_yazar.ISBN = "{isbn}";
                """
                # kitap_yazar tablosu ile yazarlar tablosu Yazar ID'leri üzerinden birleştirilir.
                # Birleşmiş tablodan kitap_yazar tablosunun ISBN sütunu isbn değişkenine eşitse
                # sorgunun sağlandığı satırların sadece yazarlar.Ad ve yazarlar.Soyad sütunları
                # tamAd olarak birleştirilerk getirir.
                cursor.execute(sqlYazalar)# SQL sorgusunun çalıştırılmasını sağlar.
                yazarList = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
                # veritabanından çekilmesini sağlar.
                yazar = [i['tamAd'] for i in yazarList]
                data[0]['yazarlarinTamami'] = yazar

                sqlKategoriler = f"""
                select Ad from kitap_kategori
                join kategoriler on kategoriler.id = kitap_kategori.KategoriID
                where kitap_kategori.ISBN = "{isbn}";
                """
                cursor.execute(sqlKategoriler)# SQL sorgusunun çalıştırılmasını sağlar.
                kategorilerList = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
                # veritabanından çekilmesini sağlar.
                kategori = [i['Ad'] for i in kategorilerList] # Veritabanından gelen veri 'kategori' adlı liste değişkeninde tutulur.
                data[0]['kategorilerinTamami'] = kategori # 'kategori' listesi data[0]a 'yazarlarinTamami' anahtar bilgisi ile atanır.

                sqlKutuphaneAdi = f"""
                select Ad from kutuphaneler where ID = {session['kutuphane']};
                """
                # kutuphaneler tablosundan ID sütunu Adminin sorumlu olduğu kütüphanenin ID sine eşitse 
                # sorguya uyan satırın Ad sütununu getirir.
                cursor.execute(sqlKutuphaneAdi)# SQL sorgusunun çalıştırılmasını sağlar.
                kutuphaneAdi = cursor.fetchall()# Yazılan sorguya uyan bütün satırların 
                # veritabanından çekilmesini sağlar.
                kutuphane = [i['Ad'] for i in kutuphaneAdi]  # Veritabanından gelen veri 'kutuphane' adlı liste değişkeninde tutulur.
                data[0]['kutuphaneAdi'] = kutuphane # 'kutuphane' listesi data[0]a 'yazarlarinTamami' anahtar bilgisi ile atanır.
                datalar.append(data[0]) # Her bir kitabın yukarıdaki bilgileri data[0]da tutulurken 
                #bütün kitapların bilgileri datalar listesinde tutulmaktadır.
            return render_template('search.html', data=datalar) # Veriler gösterilmek üzere aynı sayfaya gönderilir.
        return render_template('search.html') # Sayfa yüklendiğinde search.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.

# BUTUN KUTUPHANELERDE KITAP ARAMA - aynı
@app.route('/searchAll/', methods=["GET", "POST"])
def searchAll():
    if "username" in session:
        select = request.args.get('select')
        inputData = request.args.get('data')
        if select == 'KITAPLAR.ISBN':
            sql = f"""
            select * from kitap_kutuphane 
	        join kitaplar on kitaplar.ISBN = kitap_kutuphane.ISBN
	        where kitap_kutuphane.ISBN = "{inputData}" and kitap_kutuphane.KutuphaneID != {session['kutuphane']};
            """
            cursor.execute(sql)
            data = cursor.fetchall()
            if(not data):
                return render_template('search.html')
            sqlYazalar = f"""
            select CONCAT(yazarlar.Ad, ' ', yazarlar.Soyad) AS tamAd from kitap_yazar 
	        join yazarlar on yazarlar.ID = kitap_yazar.YazarID
            where kitap_yazar.ISBN = "{inputData}";
            """
            cursor.execute(sqlYazalar)
            yazarList = cursor.fetchall()
            yazar = [i['tamAd'] for i in yazarList]
            data[0]['yazarlarinTamami'] = yazar

            sqlKategoriler = f"""
            select Ad from kitap_kategori
	        join kategoriler on kategoriler.id = kitap_kategori.KategoriID
            where kitap_kategori.ISBN = "{inputData}";
            """
            cursor.execute(sqlKategoriler)
            kategorilerList = cursor.fetchall()
            kategori = [i['Ad'] for i in kategorilerList]
            data[0]['kategorilerinTamami'] = kategori

            sqlKutuphaneAdi = f"""
            select Ad from kutuphaneler where ID != {session['kutuphane']};
            """
            cursor.execute(sqlKutuphaneAdi)
            kutuphaneAdi = cursor.fetchall()
            kutuphane = [i['Ad'] for i in kutuphaneAdi]
            data[0]['kutuphaneAdi'] = kutuphane

            return render_template('search.html', data=data)
        elif select == 'Baslik':
            sqlBasliklar = f"""
            SELECT ISBN from kitaplar where baslik LIKE '%{inputData}%';
            """
            cursor.execute(sqlBasliklar)
            isbnler = cursor.fetchall()

            data = []
            datalar = []
            # BURADAN BASLIYOR
            for i in range(len(isbnler)):

                isbn = isbnler[i]['ISBN']
                sql = f"""
                select * from kitap_kutuphane 
                join kitaplar on kitaplar.ISBN = kitap_kutuphane.ISBN
                where kitap_kutuphane.ISBN = '{isbn}' and kitap_kutuphane.KutuphaneID != {session['kutuphane']};
                """
                cursor.execute(sql)
                data = cursor.fetchall()
                if(not data):
                    continue
                sqlYazalar = f"""
                select CONCAT(yazarlar.Ad, ' ', yazarlar.Soyad) AS tamAd from kitap_yazar 
                join yazarlar on yazarlar.ID = kitap_yazar.YazarID
                where kitap_yazar.ISBN = "{isbn}";
                """
                cursor.execute(sqlYazalar)
                yazarList = cursor.fetchall()
                yazar = [i['tamAd'] for i in yazarList]
                data[0]['yazarlarinTamami'] = yazar
                sqlKategoriler = f"""
                select Ad from kitap_kategori
                join kategoriler on kategoriler.id = kitap_kategori.KategoriID
                where kitap_kategori.ISBN = "{isbn}";
                """
                cursor.execute(sqlKategoriler)
                kategorilerList = cursor.fetchall()
                kategori = [i['Ad'] for i in kategorilerList]
                data[0]['kategorilerinTamami'] = kategori

                sqlKutuphaneAdi = f"""
                select Ad from kutuphaneler where ID != {session['kutuphane']};
                """
                cursor.execute(sqlKutuphaneAdi)
                kutuphaneAdi = cursor.fetchall()
                kutuphane = [i['Ad'] for i in kutuphaneAdi]
                data[0]['kutuphaneAdi'] = kutuphane
                datalar.append(data[0])
            # BURADA BİTİYOR

            return render_template('search.html', data=datalar)
        return render_template('search.html')
    return redirect(url_for('login'))


# KITAP EKLEME -bitti
# /add-book url'ine GET ve POST istekleri atılabilir.
@app.route('/add-book', methods=["GET", "POST"])
def add():
    # /book url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        yazarlar, kategoriler, KendiISBNsorgu,HepsiISBNsorgu = kitapSorgu() # Veritabanındaki bütün yazarlar,kategoriler 
        # ve kitapların ISBNlerini getiren fonksiyon
        if request.method == "POST": # İstek methodu kontrolü
            imd = ImmutableMultiDict(request.form) # Formdan gelen verileri ImmutableMultiDict formatına dönüştürür.
            kitapBilgileri = imd.to_dict(flat=False) 
            kendiIsbnler = [i['ISBN'] for i in KendiISBNsorgu] #KendiISBNsorgu listenin içindeki her bir elemanı 
            # isbnler sözlüğüne ISBN anahtarı ekler.
            hepsiIsbnler = [i['ISBN'] for i in HepsiISBNsorgu] #HepsiISBNsorgu listenin içindeki her bir elemanı 
            # isbnler sözlüğüne ISBN anahtarı ekler.
            
            isbn = kitapBilgileri['KitapISBN'][0] # Formdan gelen KitapISBN verisi isbn değişkeninde tutulur.
            KitapSayfaSayisi = kitapBilgileri['KitapSayfaSayisi'][0] # Formdan gelen KitapSayfaSayisi verisi KitapSayfaSayisi değişkeninde tutulur.
            KitapYayin = kitapBilgileri['KitapYayin'][0] # Formdan gelen KitapYayin verisi KitapYayin değişkeninde tutulur.
            KitapAdi = kitapBilgileri['KitapAdi'][0] # Formdan gelen KitapAdi verisi KitapAdi değişkeninde tutulur.
            miktar = kitapBilgileri['miktar'][0] # Formdan gelen miktar verisi miktar değişkeninde tutulur.

            
            kitapyazarlari = kitapBilgileri['yazarlar'][0].split(',') # Formdan gelen yazarlarin her biri kitapyazarlari listesinde tutulur.
            kitapKategorileri = kitapBilgileri['kategoriler'][0].split(',') # Formdan gelen kategoriler her biri kitapKategorileri listesinde tutulur.

            # Formdaki verilerin boş girilip girilmediği kontrolü
            if isbn=='' or KitapSayfaSayisi=='' or KitapYayin=='' or KitapAdi=='' or miktar=='' or (kitapyazarlari[0]=='') or (kitapKategorileri[0]==''):
                flash('Gerekli alanları doldurun', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('add')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.

            # Formdan girilen isbn verisinin zaten kitaplar tablosunda bulunup bulunmadığının kontrolü
            if isbn in hepsiIsbnler:
                if isbn in kendiIsbnler:
                    flash('Kitap Zaten Mevcut', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return render_template('add.html') # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
                else:
                    cats = kitapBilgileri['kategoriler'][0].split(',') # Formdan gelen kategoriler her biri kitapKategorileri listesinde tutulur.

                catsIDlist = [] # Kategorilerin idlerini tutucak liste tanımlanır
                for cat in cats: # Her bir kategoriyi dönecek döngü 
                    sql6 = f"""
                    SELECT ID from kategoriler where ad = '{cat}';
                    """
                    # kategoriler tablosunun ad sütunu döngünün şuanki değerine eşitse
                    # sorgunun sağlandığı satırın ID sütunu getirilir.
                    cursor.execute(sql6) # SQL sorgusunu çalıştırır.
                    catsIDlist.append(cursor.fetchall()) # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
                for id in catsIDlist: # Her bir kategori idyi dönecek döngü 
                    sql7 = f"""
                    INSERT INTO kitap_kategori (KategoriID, ISBN) VALUES ({id[0]['ID']}, '{isbn}');
                    """
                    # Yukarda doldurulan catsIDListnin her elemanını  kitap_kategori tablosuna ekleyecek sorgudur.
                    cursor.execute(sql7) # SQL sorgusunu çalıştırır.
                    db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
                sql9 = f""" 
                INSERT INTO kitap_kutuphane (Miktar,KutuphaneID, ISBN) 
                VALUES ({int(miktar)}, {session['kutuphane']}, '{isbn}');"""
                # Formdan gelen bilgilerle kitap_kutuphane tablosuna veri ekleyecek sorgudur.
                cursor.execute(sql9) # SQL sorgusunu çalıştırır.
                db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.

                authors = kitapBilgileri['yazarlar'][0].split(',') # Formdan gelen yazarlarin her biri kitapyazarlari listesinde tutulur.
                authorIDlist = [] # yazarların idlerini tutucak liste tanımlanır
                for auth in authors: # Her bir yazarı dönecek döngü 
                    auth.strip() # Veritabanın eklemeden önce, stringlerin etrafındaki boşlukları kaldıran fonksiyon.
                    sql10 = f"""
                    SELECT ID FROM yazarlar where CONCAT(ad, ' ', soyad) = '{auth}';
                    """
                    # yazarlar tablosunun ad ve soyad birleştirilir ve birleşmiş veri döngünün şuanki değerine eşitse
                    # sorgunun sağlandığı satırın ID sütunu getirilir.
                    cursor.execute(sql10) # SQL sorgusunu çalıştırır.
                    authorIDlist.append(cursor.fetchall()[0]) # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
                for id in authorIDlist: # Her bir yazar idyi dönecek döngü 
                    sql11 = f"""
                    INSERT INTO kitap_yazar (YazarID, ISBN) VALUES ({id['ID']}, '{isbn}');
                    """
                    # Yukarda doldurulan authorIDlist her elemanını  kitap_yazar tablosuna ekleyecek sorgudur.
                    cursor.execute(sql11) # SQL sorgusunu çalıştırır.
                    db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
                flash('Ekleme Başarlı', 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                render_template('add.html', yazarlar=yazarlar, kategoriler=kategoriler) # Veriler gösterilmek üzere aynı sayfaya gönderilir.
                    
            else: # Kitap ilk defa ekleniyorsa kontrolü
                sql5 = f"""INSERT INTO kitaplar (ISBN, Baslik, Sayfa, Yayin) VALUES ('{isbn}','{KitapAdi}',{KitapSayfaSayisi},'{KitapYayin}');
                """
                # Kitabın formdan gelen bilgilerini kitaplar tablosuna ekleyecek sorgudur.
                cursor.execute(sql5) # SQL sorgusunu çalıştırır.
                db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
                cats = kitapBilgileri['kategoriler'][0].split(',') # Formdan gelen kategoriler her biri kitapKategorileri listesinde tutulur.

                catsIDlist = [] # Kategorilerin idlerini tutucak liste tanımlanır
                for cat in cats: # Her bir kategoriyi dönecek döngü 
                    sql6 = f"""
                    SELECT ID from kategoriler where ad = '{cat}';
                    """
                    # kategoriler tablosunun ad sütunu döngünün şuanki değerine eşitse
                    # sorgunun sağlandığı satırın ID sütunu getirilir.
                    cursor.execute(sql6) # SQL sorgusunu çalıştırır.
                    catsIDlist.append(cursor.fetchall()) # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
                for id in catsIDlist: # Her bir kategori idyi dönecek döngü 
                    sql7 = f"""
                    INSERT INTO kitap_kategori (KategoriID, ISBN) VALUES ({id[0]['ID']}, '{isbn}');
                    """
                    # Yukarda doldurulan catsIDListnin her elemanını  kitap_kategori tablosuna ekleyecek sorgudur.
                    cursor.execute(sql7) # SQL sorgusunu çalıştırır.
                    db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
                sql9 = f""" 
                INSERT INTO kitap_kutuphane (Miktar,KutuphaneID, ISBN) 
                VALUES ({int(miktar)}, {session['kutuphane']}, '{isbn}');"""
                # Formdan gelen bilgilerle kitap_kutuphane tablosuna veri ekleyecek sorgudur.
                cursor.execute(sql9) # SQL sorgusunu çalıştırır.
                db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.

                authors = kitapBilgileri['yazarlar'][0].split(',') # Formdan gelen yazarlarin her biri kitapyazarlari listesinde tutulur.
                authorIDlist = [] # yazarların idlerini tutucak liste tanımlanır
                for auth in authors: # Her bir yazarı dönecek döngü 
                    auth.strip() # Veritabanın eklemeden önce, stringlerin etrafındaki boşlukları kaldıran fonksiyon.
                    sql10 = f"""
                    SELECT ID FROM yazarlar where CONCAT(ad, ' ', soyad) = '{auth}';
                    """
                    # yazarlar tablosunun ad ve soyad birleştirilir ve birleşmiş veri döngünün şuanki değerine eşitse
                    # sorgunun sağlandığı satırın ID sütunu getirilir.
                    cursor.execute(sql10) # SQL sorgusunu çalıştırır.
                    authorIDlist.append(cursor.fetchall()[0]) # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
                for id in authorIDlist: # Her bir yazar idyi dönecek döngü 
                    sql11 = f"""
                    INSERT INTO kitap_yazar (YazarID, ISBN) VALUES ({id['ID']}, '{isbn}');
                    """
                    # Yukarda doldurulan authorIDlist her elemanını  kitap_yazar tablosuna ekleyecek sorgudur.
                    cursor.execute(sql11) # SQL sorgusunu çalıştırır.
                    db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
                flash('Ekleme Başarlı', 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                render_template('add.html', yazarlar=yazarlar, kategoriler=kategoriler) # Veriler gösterilmek üzere aynı sayfaya gönderilir.
        return render_template('add.html', yazarlar=yazarlar, kategoriler=kategoriler) # Sayfa yüklendiğinde add.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.

# KITAP MIKTARI ARTIRMA- bitti
# /add-exist-book url'ine GET ve POST istekleri atılabilir.
@app.route('/add-exist-book', methods=["GET", "POST"])
def add_exist():
    # /add-exist-book'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        if request.method == 'POST': # İstek Methodu kontrolü
            kitap_ISBN = request.form['KitapISBN'] # Formdan gelen ISBN verisi 
            miktar = request.form['miktar'] # Formdan gelen miktar verisi 
            
            sql = f"""
            select kitap_kutuphane.ISBN, kitap_kutuphane.Miktar 
            from kitap_kutuphane 
            where '{kitap_ISBN}' = kitap_kutuphane.ISBN 
            and kitap_kutuphane.KutuphaneID = {session['kutuphane']}
            """
            # kitap_kutuphane tablosunun ISBN sütunu formdan gelen ISBN verisine eşitse
            # ve kitap_kutuphane tablosunun KutuphaneID sütunu adminin sorumlu olduğu kütüphanenin idsine eşitse
            # sorgunun sağlandığı satırın ISBN ve Miktar sütunu getirilir.
            cursor.execute(sql) # SQL sorgusunu çalıştırır.
            contents = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
            
            if not contents: # Veri gelmezse kitap mevcut değil demektir.
                flash('Kitap Mevcut Değil', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return render_template('add_exist.html') # Veriler gösterilmek üzere aynı sayfaya gönderilir.
            else: # Veri mevcutsa yani böyle bir kitap varsa
                try: # Hataları yakalamak için kullanılır
                    if int(miktar) < 1 : # Forma 0dan küçük bir değer girmesinin önüne geçmek için kullanılır
                        flash('Geçersiz Miktar', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                        return render_template('add_exist.html', contents=contents) # Veriler gösterilmek üzere aynı sayfaya gönderilir.
                    sql11 = f"""UPDATE kitap_kutuphane SET miktar= miktar + {miktar} WHERE ISBN = '{kitap_ISBN}' and kutuphaneID = {session['kutuphane']}"""
                    # kitap_kutuphane tablosundaki ISBN sütunu formdan gelen veriyse eşit olduğu
                    # ve kitap_kutuphane tablosundaki kutuphaneID sutunu adminin sorumlu olduğun  kutuphanenin idsinie eşit olduğu
                    # satırın miktarı miktar kadar artırılır ve güncellenir.
                    cursor.execute(sql11) # SQL sorgusunun çalıştırılmasını sağlar.
                    db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
                    flash('Ekleme Başarlı', 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return render_template('add_exist.html', contents=contents) # Veriler gösterilmek üzere aynı sayfaya gönderilir.
                except Exception: # Hata ile karşılaşılırsa 
                    flash('Geçersiz Miktar', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return render_template('add_exist.html', contents=contents) # Veriler gösterilmek üzere aynı sayfaya gönderilir.
        return render_template('add_exist.html') # Sayfa yüklendiğinde add_exist.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.

# KITAP SILME - bitti
# /delete-book url'ine GET ve POST istekleri atılabilir.
@app.route('/delete-book', methods=["GET", "POST"])
def delete_book():
    # /delete-book url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        if request.method == 'POST': # İstek Methodu Kontrolü
            kitap_ISBN = request.form['KitapISBN'] # Formdan gelen ISBN inputu
            miktar = request.form['miktar'] # Formdan gelen silinecek miktar inputu
            sql = f"""
            select kitap_kutuphane.ISBN, kitap_kutuphane.Miktar 
            from kitap_kutuphane 
            where '{kitap_ISBN}' = kitap_kutuphane.ISBN 
            and kitap_kutuphane.KutuphaneID = {session['kutuphane']}
            """
            # kitap_kutuphane tablosunun ISBN sütunu inputtan gelen kitap_ISBN verisine eşitse
            # ve kitap_kutuphane tablosunun KutuphaneID sütunu Adminin sorumlu olduğu kütüphanenin ID'sine eşitse 
            # sorgunun sağlandığı satırların ISBN ve miktar sütununu getirir.

            cursor.execute(sql) # SQL sorgusunun çalıştırılmasını sağlar.
            contents = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            if not contents: # Veri mevcut mu kontrolü yapılır.
                flash('Kitap Mevcut Değil', 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return render_template('delete_book.html') # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
            else: # Veri mevcutsa
                contents = contents[0]
                if int(contents['Miktar']) >= int(miktar): # Kitabın kütüphanedeki miktarının 
                    # silinmek istenen miktardan fazla olması kontrol ediyor bu sayede veritabanında hata oluşmasının önüne geçiliyor
                    sql11 = f"""UPDATE kitap_kutuphane SET miktar = miktar - {int(miktar)} WHERE ISBN = '{kitap_ISBN}' and kutuphaneID = {session['kutuphane']}"""
                    # kitap_kutuphane tablosunun ISBN sütunu inputtan gelen kitap_ISBN verisine eşitse
                    # ve kitap_kutuphane tablosunun KutuphaneID sütunu Adminin sorumlu olduğu kütüphanenin ID'sine eşitse 
                    # sorgunun sağlandığı satırların miktar bilgisi veritabanındaki 
                    # miktar bilginsinden  silinmek istenen miktar bilgisini çıkararak güncelleniyor.
                    cursor.execute(sql11) # SQL sorgusunun çalıştırılmasını sağlar.
                    db.connection.commit()# Yazılan sorguya uyan bütün satırların 
                    # veritabanından çekilmesini sağlar.
                    flash(
                        f"{miktar} adet kitap başarıyla silindi.\nKalan kitap sayısı: {contents['Miktar'] - int(miktar)}", 'info')
                        # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return render_template('delete_book.html') # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
                else: # Silinmek istenen miktar veritabanındaki mevcut kitap miktarından fazlaysa silmez ve ekrana bir hata mesajı basar
                    flash(
                        f"Silme işlemi başarısız. \nMevcut kitap sayısı: {contents['Miktar']}", 'danger')
                        # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return render_template('delete_book.html') # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
        return render_template('delete_book.html') # Sayfa yüklendiğinde delete_book.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.

# TESLIM ALMA- bitti
# /receive-book url'ine GET ve POST istekleri atılabilir.
@app.route('/receive-book', methods=["GET", "POST"])
def receive_book():
    # /receive-book url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        if request.method == 'POST': # İstek metodu kontrolü
            imd = ImmutableMultiDict(request.form) # Formdan gelen veriler ImmutableMultiDict formatına dönüştürülür.
            bilgiler = imd.to_dict(flat=False)
            eposta = bilgiler['uyeeposta'] # Formdan gelen email inputu
            telefon = bilgiler['uyetel'] # Formdan gelen telefon inputu

            sqlUyeID = f"""select ID from uyeler where Eposta='{eposta[0]}' and Telefon='{telefon[0]}';"""
            # uyeler tablosunun Eposta sütunu inputtan gelen eposta verisine eşitse
            # ve uyeler tablosunun Telefon sütunu inputtan gelen telefon verisine eşitse
            # sorgunun sağlandığı satırların ID sütununu getirir.

            cursor.execute(sqlUyeID) # SQL sorgusunun çalıştırılmasını sağlar.
            uyeID = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.

            if not uyeID: # Veri mevcut mu kontrolü yapılır
                flash(f"İşlem başarısız bilgileri kontrol edin ", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('receive_book')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.

            

            sqlTeslim = f"""UPDATE
	        kitap_emanet 
            SET kitap_emanet.Durum = 1,kitap_emanet.TeslimTarih = NOW()
            where 
            kitap_emanet.UyeID= {uyeID[0]['ID']}
            and kitap_emanet.Durum=0 
            and kitap_emanet.ISBN='{bilgiler['kitapisbn'][0]}'
            and kitap_emanet.KutuphaneID = {session['kutuphane']};"""
            
            # kitap_emanet tablosunun Durum sütunu 0'a(teslim edilmemiş kitapları temsil eder) eşit olduğu
            # ve kitap_emanet tablosunun ISBN sütunu formdan gelen ISBN verisine eşit olduğu
            # ve kitap_emanet tablosunun UyeID sütunu veritabanından gelen üyeIDsine eşit olduğu
            # ve kitap_emanet tablosunun kutuphaneID sütunu Adminin sorumlu olduğu kütüphanenin ID'sine eşit olduğu
            # satırın kitap_emanet tablosundaki Durum sutununu 1 olarak güncelle, 
            # satırın kitap_emanet tablosundaki TeslimTarih sutununu o anın tarihi olarak güncelle, 
            
            

            cursor.execute(sqlTeslim) # SQL sorgusunun çalıştırılmasını sağlar.
            db.connection.commit() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            rows_affected=cursor.rowcount # Çalıştırılan sorgudan sonra kaç satırın etkilendiğini tutmak için tanımlanan değişken
            if(rows_affected==0): # Eğer 0 satır etkilenmişse böyle bir kitap emanet edilmemiştir.
                flash(f"Böyle bir kitap emanet edilmemiş.", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('receive_book')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
            else: # Eğer 0dan fala satır etkilenmişse kitap emanet işlemi yapılmıştır
                sqlMiktarArtirma=f"""UPDATE kitap_kutuphane
                SET kitap_kutuphane.Miktar = kitap_kutuphane.Miktar+1 
                where kitap_kutuphane.KutuphaneID = {session['kutuphane']};"""
                # kitap_kutuphane tablosunun KutuphaneID sütunu Adminin sorumlu olduğu kütüphanenin ID'sine eşit olduğu
                # satırın Miktar sutununu 1 artırarak  güncelle, 
                cursor.execute(sqlMiktarArtirma) # SQL sorgusunun çalıştırılmasını sağlar.
                db.connection.commit() # Yazılan sorguya uyan bütün satırların 
                flash(f"Teslim Alma işlemi başarılı.", 'success') # Eğer bir satır etkilendiyse Teslim işlemi başarılıdır ve flash tanımlanır
                return redirect(url_for('receive_book')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.

        return render_template('teslimAl.html') # Sayfa yüklendiğinde teslimAl.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.


# UYE SILME - bitti
# /delete-member url'ine GET ve POST istekleri atılabilir.
@app.route('/delete-member', methods=["GET", "POST"])
def delete_member():
    # /delete-member url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        if request.method == 'POST': # İstek methodu kontrolü
            imd = ImmutableMultiDict(request.form) # Formdan gelen veriler ImmutableMultiDict formatına dönüştürülür.
            bilgiler = imd.to_dict(flat=False)
            
            eposta = bilgiler['uyeeposta'] # Formdan gelen üye eposta bilgisi
            telefon = bilgiler['uyetel'] # Formdan gelen üye telefon bilgisi

            sqlUyeID = f"""select ID from uyeler where Eposta='{eposta[0]}' and Telefon='{telefon[0]}';"""
            # uyeler tablosunun Eposta sütunu inputtan gelen eposta verisine eşitse
            # ve uyeler tablosunun Telefon sütunu inputtan gelen telefon verisine eşitse
            # sorgunun sağlandığı satırların ID sütununu getirir.
            cursor.execute(sqlUyeID) # SQL sorgusunun çalıştırılmasını sağlar.
            uyeID = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
            
            if not uyeID: # Herhangi bir veri gelmemişse(Yani üye mevcut değilse);
                flash(f"İşlem başarısız bilgileri kontrol edin ", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('delete_member')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.

            sqlUyeKontrol = f"""SELECT * FROM kitap_emanet where kitap_emanet.UyeID={uyeID[0]['ID']} and kitap_emanet.Durum=0;"""
            # kitap_emanet tablosunun UyeID sütunu veritabanından çekilen uyeID verisine eşitse
            # ve kitap_emanet tablosunun Durum sütunu 0'a(teslim edilmemiş kitapları temsil eder) eşitse
            # sorgunun sağlandığı satırları getirir.
            cursor.execute(sqlUyeKontrol) # SQL sorgusunu çalıştırır.
            uyeEmanetTablosu = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
            
            if uyeEmanetTablosu: # Eğer böyle bir veri mevcutsa(üyenin teslim etmediği kitaplar mevcut demektir) üye silme işlemi yapılmaz.
                flash(f"Üye silme işlemi başarısız. Teslim Edilmemiş Kitap Mevcut", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('delete_member')) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.

            
            # ancak böyle bir veri gelmezse(yani üye bütün emanetlerini teslim ettiyse)
            

            sqlUyeSil = f"""DELETE adresler
            FROM uyeler
            LEFT JOIN adresler ON uyeler.AdresID = adresler.ID
            LEFT JOIN kitap_emanet on uyeler.ID = kitap_emanet.UyeID
            WHERE uyeler.ID = {uyeID[0]['ID']};"""
            # Önce uyeler tablosu ile adresler tablosu Adres ID üzerinden 
            # sonra adresler tablosu ile kitap_emanet tablosu Uye ID üzerinden birleştirilir.
            # ve bu birleşmiş tablonun uyeler tablosunun ID sütunu veritabanından çekilen uyeID verisine eşitse
            # birleşmiş tablonun o satırı silinir ve böylece üye; üyeler,adresler ve kitap_emanet tablosundan aynı anda silinmiş olur.

            cursor.execute(sqlUyeSil) # SQL sorgusunu çalıştırır.
            db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
            flash(f"Üye silme işlemi başarılı.", 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
            return redirect(url_for('delete_member')) # Aynı sayfaya tekrar yönlendirilir

        return render_template('uyeSil.html') # Site açıldığında ekrana uyeSil.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirir.


# YAZAR EKLEME - bitti
# /add-author url'ine GET ve POST istekleri atılabilir.
@app.route('/add-author', methods=["GET", "POST"])
def yazarekle():
    # /add-author url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        if(request.method == "POST"): # İstek methodu kontrolü
            imd = ImmutableMultiDict(request.form) # Formdan gelen veriler ImmutableMultiDict formatına dönüştürülür.
            yazarBilgi = imd.to_dict(flat=False)
            sql = f"""
            INSERT INTO yazarlar (ad, soyad) VALUES ('{yazarBilgi['YazarName'][0]}', '{yazarBilgi['YazarSurname'][0]}');
            """
            # Yazarın formdan gelen ad ve soyad bilgilerini yazarlar tablosuna ekleyecek sorgudur.
            cursor.execute(sql) # SQL sorgusunu çalıştırır.
            db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.
            flash('Yazar Ekleme Başarlı', 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
            render_template('yazarEkle.html') # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
        return render_template('yazarEkle.html') # Site açıldığında yazarEkle.html dosyası ekrana basılır.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.


# KITAP EMANET- bitti
# /deposit-book/<ISBN> url'ine GET ve POST istekleri atılabilir.
@app.route('/deposit-book/<ISBN>', methods=["GET", "POST"])
def kitap_emanet(ISBN):
    # /deposit-book/<ISBN> url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        if(request.method == "POST"): # İstek methodu kontrolü
            imd = ImmutableMultiDict(request.form) # Formdan gelen verileri ImmutableMultiDict formatına dönüştürür.
            uyeEmanetBilgi = imd.to_dict(flat=False)
            eposta = uyeEmanetBilgi['uyeeposta'] # Formdan gelen email inputu
            telefon = uyeEmanetBilgi['uyetel'] # Formdan gelen telefon inputu

            sqlUyeID = f"""select ID from uyeler where Eposta='{eposta[0]}' and Telefon='{telefon[0]}';"""
            # uyeler tablosunun Eposta sütunu inputtan gelen eposta verisine eşitse
            # ve uyeler tablosunun Telefon sütunu inputtan gelen telefon verisine eşitse
            # sorgunun sağlandığı satırların ID sütununu getirir.
            cursor.execute(sqlUyeID) # SQL sorgusunun çalıştırılmasını sağlar.
            uyeID = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            if not uyeID: # Veri mevcut mu kontrolü yapılır
                flash(f"İşlem başarısız üye bilgilerini kontrol edin ", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('details', book=ISBN, lib=session['kutuphane'])) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.

            sql = f"""
            select kitap_kutuphane.ISBN, kitap_kutuphane.Miktar 
            from kitap_kutuphane 
            where '{ISBN}' = kitap_kutuphane.ISBN 
            and kitap_kutuphane.KutuphaneID = {session['kutuphane']}
            """
            # kitap_kutuphane tablosunun ISBN sütunu inputtan gelen ISBN verisine eşitse
            # ve kitap_kutuphane tablosunun KutuphaneID adminin sorumlu olduğu kütüphanenin idsine eşitse
            # sorgunun sağlandığı satırların ISBN ve Miktar sütununu getirir.
            cursor.execute(sql) # SQL sorgusunun çalıştırılmasını sağlar.
            contents = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
            # veritabanından çekilmesini sağlar.
            contents = contents[0]
            if int(contents['Miktar']) >= 1: # Miktar kontrolü yapılır (Emanet işleminin gerçekleşebilmesi için en az bir kitap mevcut olmalıdır)
                uyeID = uyeID[0]['ID']
                sqlEmanetDurum = f"""SELECT * FROM kitap_emanet WHERE ISBN='{ISBN}' and Durum=0 and UyeID={uyeID} and KutuphaneID={session['kutuphane']};"""
                # kitap_emanet tablosunun ISBN sütunu inputtan gelen ISBN verisine eşitse
                # ve kitap_emanet tablosunun Durum sütunu 0'a(teslim edilmemiş kitapları temsil eder) eşitse
                # ve kitap_emanet tablosunun UyeID sütunu veritabanından gelen uyeID'ye eşitse
                # ve kitap_emanet tablosunun KutuphaneID  sütunu adminin sorumlu olduğu kütüphanenin idsine eşitse
                # sorgunun sağlandığı satırlar getirilir.
                cursor.execute(sqlEmanetDurum) # SQL sorgusunun çalıştırılmasını sağlar.
                emanetDurum = cursor.fetchall() # Yazılan sorguya uyan bütün satırların 
                # veritabanından çekilmesini sağlar.
                if emanetDurum: # Eğer böyle bir veri varsa yani bu kitap daha önce bu kullanıcıya verilmişse 
                    flash(f"Bu kitap üyede mevcut", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                    return redirect(url_for('details', book=ISBN, lib=session['kutuphane'])) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
                # Eğer böyle bir yoksa yani bu kitap daha önce bu kullanıcıya verilmemişse 
                sqlKitapEmanet = f"""insert into kitap_emanet (AlimTarih,SonTeslimTarih,KutuphaneID,UyeID,ISBN) 
                values (NOW(),DATE_ADD(NOW(), INTERVAL +30 DAY),{session['kutuphane']},{uyeID},'{ISBN}');"""
                # kitap_emanet tablosuna tarih verileri ve formdan gelen biligileri ekleyecek sorgudur.
                cursor.execute(sqlKitapEmanet) # SQL sorgusunun çalıştırılmasını sağlar.
                db.connection.commit() # Veritabanında yapılan değişiklikleri kaydeder.

                sqlMiktarUpdate = f"""UPDATE kitap_kutuphane SET miktar= miktar - 1 WHERE ISBN = '{ISBN}' and kutuphaneID = {session['kutuphane']};"""
                # kitap_kutuphane tablosundaki ISBN sütunu formdan gelen veriyse eşit olduğu
                # ve kutuphaneID sutunu adminin sorumlu olduğun  kutuphanenin idsinie eşit olduğu
                # satırın miktarı bir azaltılarak güncellenir.
                cursor.execute(sqlMiktarUpdate) # SQL sorgusunun çalıştırılmasını sağlar.
                db.connection.commit() # Yazılan sorguya uyan bütün satırların 
                # veritabanından çekilmesini sağlar.

                flash(f"Emanet işlemi başarılı.", 'success') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('details', book=ISBN, lib=session['kutuphane'])) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
            else:
                flash(f"Emanet verme işlemi başarısız. \nMevcut kitap sayısı: {contents['Miktar']}", 'danger') # Ekrana bilgilendirme mesajı göstermek için flash tanımlanır.
                return redirect(url_for('details', book=ISBN, lib=session['kutuphane'])) # Ekrana bilgilendirme mesajını basmak aynı sayfaya yönlendirilir.
            
        return render_template('details.html') # Sayfa yüklendiğinde details.html dosyasını ekrana basar.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.


# KITAP DETAYLARI- bitti
# /details/<lib>/<book> url'ine GET ve POST istekleri atılabilir.
@app.route('/details/<lib>/<book>')
def details(lib, book):
    # /details/<lib>/<book> url'inde çalışacak fonksiyon
    if "username" in session: # Oturum kontrolü
        isbn = book # Sayfaya GET methodu ile gelen argüman isbn isimli br değişkende tutulur
        sql = f"""
        select * from kitap_kutuphane 
        join kitaplar on kitaplar.ISBN = kitap_kutuphane.ISBN
        where kitap_kutuphane.ISBN = "{isbn}" and kitap_kutuphane.KutuphaneID={lib};
        """
        # kitap_kutuphane tablosu kitaplar tablosu ile ISBN sütunu üzerinden birleştirilir.
        # birleştirilmiş tablonun tablosunun kitap_kutuphane tablosunun ISBN sütunu argüman olarak gelen isbn verisine eşitse
        # birleştirilmiş tablonun tablosunun kitap_kutuphane tablosunun kutuphaneID sütunu adminin sorumlu olduğu kütüphanenin idsine eşitse
        # sorgunun sağlandığı satır  getirilir.
        cursor.execute(sql) # SQL sorgusunu çalıştırır.
        data = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.

        if(not data): # Veri yoksa 
            return render_template('search.html') # Aynı sayfaya yönlendirilir.
        # varsa

        sqlYazalar = f"""
        select CONCAT(yazarlar.Ad, ' ', yazarlar.Soyad) AS tamAd from kitap_yazar 
        join yazarlar on yazarlar.ID = kitap_yazar.YazarID
        where kitap_yazar.ISBN = "{isbn}";
        """
        # kitap_yazar tablosu yazarlar tablosu ile yazar ID'ler üzerinden birleştirilir.
        # birleştirilmiş tablonun kitap_yazar ISBN sütunu argüman olarak gelen isbn verisine eşitse
        # sorgunun sağlandığı satırın yazar adı ve yazar soyadı birleştirilerek tamAd olarak  getirilir.
        cursor.execute(sqlYazalar) # SQL sorgusunu çalıştırır.
        yazarList = cursor.fetchall()  # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
        yazar = [i['tamAd'] for i in yazarList] # Veritabanından gelen veri 'yazarList' adlı yazar liste değişkeninde tutulur.
        data[0]['yazarlarinTamami'] = yazar # Details sayfasına yönlendirilmek üzere 'yazar' listesi data[0]a 'yazarlarinTamami' anahtar bilgisi ile atanır.

        sqlKategoriler = f"""
        select Ad from kitap_kategori
        join kategoriler on kategoriler.id = kitap_kategori.KategoriID
        where kitap_kategori.ISBN = "{isbn}";
        """
        # kitap_kategori tablosu  kategoriler ile kategori ID'ler üzerinden birleştirilir.
        # birleştirilmiş tablonun  kitap_kategori tablosunun ISBN sütunu argüman olarak gelen isbn verisine eşitse
        # sorgunun sağlandığı satırın Ad sütunu  getirilir.
        cursor.execute(sqlKategoriler)  # SQL sorgusunu çalıştırır.
        kategorilerList = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
        kategori = [i['Ad'] for i in kategorilerList] # Veritabanından gelen veri 'kategorilerList' adlı kategori liste değişkeninde tutulur.
        data[0]['kategorilerinTamami'] = kategori # Details sayfasına yönlendirilmek üzere 'kategori' listesi data[0]a 'kategorilerinTamami' anahtar bilgisi ile atanır.

        sqlKutuphaneAdi = f"""
        select Ad from kutuphaneler where ID = {lib};
        """
        # kutuphaneler tablosunun ID sütunu argüman olarak gelen kutuphane idsine eşitse
        # sorgunun sağlandığı satırın Ad sütunu  getirilir.
        cursor.execute(sqlKutuphaneAdi)  # SQL sorgusunu çalıştırır.
        kutuphaneAdi = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
        kutuphane = [i['Ad'] for i in kutuphaneAdi] # Veritabanından gelen veri 'kutuphaneAdi' adlı listeden kutuphane liste değişkeninde tutulur.
        data[0]['kutuphaneAdi'] = kutuphane # Details sayfasına yönlendirilmek üzere 'kutuphane' listesi data[0]a 'kutuphaneAdi' anahtar bilgisi ile atanır.

        sqlKutuphaneAdresi = f"""
        SELECT CONCAT(adresler.İkamet_adresi,", ",adresler.Ilce,"/", adresler.Il) as tamAdres FROM kutuphaneler 
        join adresler on kutuphaneler.AdresID = adresler.ID
        where kutuphaneler.ID = {lib};
        """
        # kutuphaneler tablosu  adresler ile Adres ID'ler üzerinden birleştirilir.
        # birleştirilmiş tablonun  kutuphaneler tablosunun ID sütunu argüman olarak gelen kutuphane idsine  eşitse
        # sorgunun sağlandığı satırın ikamet adresi,ilce ve il sütunu birleştirilerek  getirilir.
        cursor.execute(sqlKutuphaneAdresi) # SQL sorgusunu çalıştırır.
        kutuphaneAdresi = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
        kutuphaneTamAdresi = [i['tamAdres'] for i in kutuphaneAdresi] # Veritabanından gelen veri 'kutuphaneAdresi' adlı listeden kutuphaneTamAdresi anahtar liste değişkeninde tutulur.
        data[0]['kutuphaneTamAdresi'] = kutuphaneTamAdresi # Details sayfasına yönlendirilmek üzere 'kutuphane' listesi data[0]a 'kutuphaneAdi' anahtar bilgisi ile atanır.

        return render_template('details.html', details=data) # Veriler gösterilmek üzere details.html sayfasına gönderilir.
    return redirect(url_for('login')) # Oturum açılmamışsa login sayfasına yönlendirilir.


def adminId():
    sql = f"""select KutuphaneID from adminler where kullaniciAdi = '{session['username']}'"""
    # Oturum açan adminin sorumlu olduğu kütüphanenin ID bilgisini Adminler tablosundan getirecek sorgudur.
    cursor.execute(sql) # SQL sorgusunu çalıştırır.
    contents = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
    session['kutuphane'] = contents[0]['KutuphaneID'] # Oturum açan adminin sorumlu olduğu kütüphanenin IDsi session a kaydedilir


def kitapSorgu():
    sql = """SELECT ad, soyad FROM yazarlar"""
    # yazarlar tablosundan bütün yazarların ad ve soyad bilgilerini getirecek sorgudur.
    sql2 = """SELECT ad FROM kategoriler"""
    # kategoriler tablosundan bütün kategorilerin ad bilgilerini getirecek sorgudur.
    sql3 = f""" SELECT kitaplar.ISBN FROM kitaplar 
    JOIN kitap_kutuphane on 
    kitaplar.ISBN = kitap_kutuphane.ISBN where kitap_kutuphane.KutuphaneID={session['kutuphane']} """
    sql4 = """ SELECT ISBN FROM kitaplar """
    # kitaplar tablosu kitap_kutuphane tablosu ile ISBN'ler üzerinden birleştirilir.
    # birleştirilmiş tablonun  kitap_kutuphane tablosunun KutuphaneID sütunu session'a kaydedilen kutuphane id'ye  eşitse
    # sorgunun sağlandığı satırların kitaplar.ISBN sütunu getirilir.
    cursor.execute(sql) # SQL sorgusunu çalıştırır.
    yazarlar = cursor.fetchall()
    cursor.execute(sql2) # SQL sorgusunu çalıştırır.
    kategoriler = cursor.fetchall()  # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
    cursor.execute(sql3) # SQL sorgusunu çalıştırır.
    KendiISBNsorgu = cursor.fetchall()  # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
    cursor.execute(sql4) # SQL sorgusunu çalıştırır.
    HepsiISBNsorgu = cursor.fetchall()  # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
    return yazarlar, kategoriler, KendiISBNsorgu,HepsiISBNsorgu # Veritabanından gelen veriler fonksiyonun çağırıldığı yerlere return edilir.


def uyeSorgu():
    sql = """SELECT * FROM uyeler"""
    # uyeler tablosundaki bütün üyelerin bütün bilgilerini getirecek sorgudur.
    cursor.execute(sql) # SQL sorgusunu çalıştırır.
    uyelerData = cursor.fetchall() # Yazılan sorguya uyan bütün satırların veritabanından çekilmesini sağlar.
    return uyelerData # Veritabanından gelen veriler fonksiyonun çağırıldığı yerlere return edilir.


if __name__ == "__main__":
    app.run(debug=True)
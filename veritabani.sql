create database veritabani_zorunlu_proje_son;

USE veritabani_zorunlu_proje_son;

CREATE TABLE adresler(
	ID int NOT NULL AUTO_INCREMENT,
	Il varchar(100) NOT NULL, 
	Ilce varchar(100) NOT NULL, 
	İkamet_Adresi varchar(250) NOT NULL,
	PostaKodu varchar(100) NOT NULL, 
	PRIMARY KEY (ID)
	
);


CREATE TABLE uyeler(
	ID int NOT NULL AUTO_INCREMENT,
	Ad varchar(100) NOT NULL,
	Soyad varchar(100) NOT NULL,
	Eposta varchar(100) NOT NULL,
	Telefon varchar(100) NOT NULL,
	AdresID int NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY (AdresID) REFERENCES ADRESLER(ID)
	ON DELETE CASCADE
);


CREATE TABLE kitaplar(
	ISBN varchar(100) NOT NULL,
	Baslik varchar(100) NOT NULL,
	Sayfa int NOT NULL,
	Yayin varchar(100) NOT NULL,
	PRIMARY KEY (ISBN)
);


CREATE TABLE kategoriler(
	ID int NOT NULL AUTO_INCREMENT,
	Ad varchar(100) NOT NULL,
	PRIMARY KEY (ID)
);


CREATE TABLE kutuphaneler(
	ID int NOT NULL AUTO_INCREMENT,
	Ad varchar(100) NOT NULL,
	AdresID int NOT NULL UNIQUE,
	PRIMARY KEY (ID),
	FOREIGN KEY (AdresID) REFERENCES ADRESLER(ID)
);

CREATE TABLE yazarlar(
	ID int NOT NULL AUTO_INCREMENT,
	Ad varchar(100) NOT NULL,
	Soyad varchar(100) NOT NULL,
	PRIMARY KEY (ID)
);

CREATE TABLE kitap_yazar(
	ID int NOT NULL AUTO_INCREMENT,
	YazarID int NOT NULL,
	ISBN varchar(100) NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY (YazarID) REFERENCES YAZARLAR(ID),
	FOREIGN KEY (ISBN) REFERENCES KITAPLAR(ISBN)
);

CREATE TABLE kitap_kategori(
	ID int NOT NULL AUTO_INCREMENT,
	KategoriID int NOT NULL,
	ISBN varchar(100) NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY (KategoriID) REFERENCES KATEGORILER(ID),
	FOREIGN KEY (ISBN) REFERENCES KITAPLAR(ISBN)
);


CREATE TABLE kitap_kutuphane(
	ID int NOT NULL AUTO_INCREMENT,
	Miktar int NOT NULL,
	KutuphaneID int NOT NULL,
	ISBN varchar(100) NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY (KutuphaneID) REFERENCES KUTUPHANELER(ID),
	FOREIGN KEY (ISBN) REFERENCES KITAPLAR(ISBN)
);


CREATE TABLE kitap_emanet(
	EmanetNo int NOT NULL AUTO_INCREMENT,
	AlimTarih DATETIME NOT NULL,
	Durum tinyint(1) NOT NULL DEFAULT 0,
	SonTeslimTarih datetime DEFAULT NULL,
	TeslimTarih DATETIME DEFAULT NULL,
	KutuphaneID int NOT NULL,
	UyeID int NOT NULL,
	ISBN varchar(100) NOT NULL,
	PRIMARY KEY (EmanetNo),
	FOREIGN KEY (KutuphaneID) REFERENCES KUTUPHANELER(ID),
	FOREIGN KEY (ISBN) REFERENCES KITAPLAR(ISBN),
	FOREIGN KEY (UyeID) REFERENCES UYELER(ID)
	ON DELETE CASCADE
);

create table adminler(
	ID int NOT NULL AUTO_INCREMENT,
	KullaniciAdi varchar(100) NOT NULL,
	Sifre varchar(100) NOT NULL,
	KutuphaneID int NOT NULL,
	PRIMARY KEY (ID),
    FOREIGN KEY (KutuphaneID) REFERENCES kutuphaneler(ID)
);


INSERT INTO `adresler` (`ID`, `Il`, `Ilce`, `PostaKodu`, `İkamet_Adresi`) VALUES
(1, 'Adana', 'Seyhan', '41001', 'bayramoglu mah. 12 sokak 12/18'),
(3, 'Ankara', 'Mamak', '32003', 'orhangazi mah. 11 sokak 12/16'),
(4, 'Ankara', 'Ulus', '12004', 'seyhan mah. 11 sokak 12/12'),
(5, 'Ankara', 'Mamak', '01020', 'şimşek mah. 11 sokak 2/16'),
(6, 'Bilecik', 'Gölpazarı', '06546', 'aslanbey mah. 11 sokak 12/16'),
(7, 'Balıkesir', 'Ayvalık', '01631', 'kuzu mah. 11 sokak 12/16'),
(8, 'Çorum', 'Dodurga', '01612', 'koç mah. 11 sokak 12/16'),
(10, 'Bursa', 'Gürsu', '01668', 'kaya mah. 11 sokak 12/16'),
(11, 'Ankara', 'Mamak', '01000', 'kangal mah. 11 sokak 12/16'),
(12, 'Çankırı', 'Yapraklı', '01686', 'çam mah. 11 sokak 12/16'),
(13, 'Çanakkale', 'Gelibolu', '08568', 'murat mah. 98 sokak 12/12'),
(15, 'Burdur', 'Tefenni', '01669', 'aslan mah. 323 sokak 12/25'),
(17, 'Bitlis', 'Merkez', '12313', 'asdasdasd'),
(20, 'Bursa', 'Nilüfer', '16130', 'Karaman Mah. Nilüfer/Bursa');

INSERT INTO `uyeler` (`ID`, `Ad`, `Soyad`, `Eposta`, `Telefon`, `AdresID`) VALUES
(1, 'Selçuk', 'Şan', 'Selcuk@gmail.com', '05430000000', 1),
(4, 'Fatih Eren', 'Erol', 'Fatih@gmail.com', '05433333333', 3),
(5, 'Saner', 'Tolak', 'taner@gmail.com', '12313123213', 6),
(6, 'Selçuk', 'Şan', 'selcuk1330@gmail.com', '+3345345418', 7),
(7, 'Selçuk', 'Şan', 'sel@gmail.com', '+905438478618', 8),
(10, 'gurhan', 'tezer', 'gurhan@gmail.com', '+90512318', 15),
(12, '123123', '123', 'asda@gmail.com', '+123123', 17),
(15, 'Mustafa', 'Eren', 'mustafaeren790@gmail.com', '05079747815', 20);


INSERT INTO `kitaplar` (`ISBN`, `Baslik`, `Sayfa`, `Yayin`) VALUES
('9786051770901', 'Beyaz Zambaklar Ülkesinde', 152, 'İSKELE YAYINCILIK'),
('9786052980811', 'Körlük', 336, 'Kırmızı Kedi'),
('9786053757818', 'Fahrenheit 451', 208, 'İthaki Yayınları'),
('9786058758872', 'Python', 544, 'DİKEYEKSEN YAYINCILIK'),
('9789712350718533', 'deneme4', 136, 'deneme4'),
('9789750718533', 'On Bir Dakika', 352, 'CAN YAYINLARI'),
('9789750726439', 'Şeker Portakalı', 184, 'CAN YAYINLARI'),
('9789750738609', 'Gazi Mustafa Kemal Atatürk', 182, 'CAN YAYINLARI'),
('9789752430297', '1984', 480, 'KRONİK KİTAP'),
('9789752430990', 'Bir Ömür Nasıl Yaşanır', 288, 'Kronik Kitap'),
('9789754587173', 'Devlet', 372, 'TÜRKİYE İŞ BANKASI KÜLTÜR YAYINLARI'),
('9789755705859', 'Fareler ve İnsanlar', 111, 'Sel Yayıncılık'),
('9789756902165', 'Cesur Yeni Dünya', 272, 'İthaki Yayınları'),
('BTU', 'BTU', 1, 'BTU'),
('Mustafa', 'Mustafa Eren', 123, 'Mustafa'),
('VTYS', 'VTYS', 4, 'BTU'),
('VTYS2', 'VTYS2', 4, 'BTU'),
('YMS', 'YMS', 123, 'YMS');


INSERT INTO `kategoriler` (`ID`, `Ad`) VALUES
(1, 'Tarih'),
(2, 'Edebiyat'),
(3, 'Doğa Bilimleri ve Matematik'),
(4, 'Felsefe'),
(5, 'Din'),
(6, 'Toplum Bilimleri'),
(7, 'Teknoloji');



INSERT INTO `kutuphaneler` (`ID`, `Ad`, `AdresID`) VALUES
(1, 'Ulus Kütüphanesi', 4),
(2, 'Mamak Kütüphanesi', 5);




INSERT INTO `yazarlar` (`ID`, `Ad`, `Soyad`) VALUES
(1, 'İlber', 'Ortaylı'),
(2, 'Platon', ''),
(3, 'Mustafa', 'Başer'),
(4, 'George', 'Orwell'),
(5, 'Grigory', 'Petrov'),
(6, 'Jose Mauro', 'De Vasconcelos'),
(7, 'Paulo ', 'Coelho'),
(8, 'Şeyma', 'Subaşı'),
(9, 'selçuk', 'şan'),
(10, 'Turgay', 'Bilgin'),
(11, 'Celal', 'Şengör'),
(12, 'Sabahattin', 'Ali'),
(13, 'Atatürk', ''),
(14, 'Mustafa ', 'Eren'),
(15, 'Jose', 'Saramago'),
(16, 'John', 'Steinbeck'),
(17, 'Aldous', 'Huxley'),
(18, 'Ray', 'Bradbury'),
(19, 'Kerem', 'Ersu'),
(20, 'Fatih Eren ', 'Erol');

INSERT INTO `kitap_yazar` (`ID`, `YazarID`, `ISBN`) VALUES
(1, 5, '9786051770901'),
(2, 3, '9786058758872'),
(3, 4, '9789752430297'),
(4, 7, '9789750718533'),
(5, 6, '9789750726439'),
(6, 1, '9789750738609'),
(7, 2, '9789754587173'),
(30, 15, '9786052980811'),
(31, 16, '9789755705859'),
(32, 17, '9789756902165'),
(33, 18, '9786053757818'),
(34, 19, 'YMS'),
(35, 14, 'YMS'),
(36, 9, 'YMS'),
(37, 20, 'YMS'),
(38, 1, '9789752430990'),
(39, 14, 'BTU'),
(40, 9, 'BTU'),
(41, 14, 'VTYS'),
(42, 19, 'VTYS'),
(43, 9, 'VTYS'),
(44, 20, 'VTYS'),
(45, 14, 'VTYS2'),
(46, 19, 'VTYS2'),
(47, 9, 'VTYS2'),
(48, 20, 'VTYS2');


INSERT INTO `kitap_kategori` (`ID`, `KategoriID`, `ISBN`) VALUES
(1, 1, '9789752430297'),
(2, 1, '9786051770901'),
(3, 2, '9789750718533'),
(4, 2, '9789750726439'),
(5, 2, '9789750738609'),
(6, 4, '9789754587173'),
(7, 7, '9786058758872'),
(51, 2, '9786052980811'),
(52, 2, '9789755705859'),
(53, 4, '9789756902165'),
(54, 2, '9789756902165'),
(55, 6, '9786053757818'),
(56, 1, '9786053757818'),
(57, 7, 'YMS'),
(58, 6, '9789752430990'),
(59, 1, '9789752430990'),
(60, 2, '9789752430990'),
(61, 7, 'Mustafa'),
(62, 7, 'BTU'),
(63, 7, 'VTYS'),
(64, 5, 'VTYS'),
(65, 7, 'VTYS2'),
(66, 5, 'VTYS2');



INSERT INTO `kitap_kutuphane` (`ID`, `Miktar`, `KutuphaneID`, `ISBN`) VALUES
(1, 1, 1, '9786051770901'),
(2, 6, 2, '9786051770901'),
(3, 10, 1, '9786058758872'),
(4, 7, 2, '9786058758872'),
(5, 11, 1, '9789752430297'),
(6, 5, 2, '9789752430297'),
(7, 16, 1, '9789750718533'),
(8, 6, 2, '9789750718533'),
(9, 9, 1, '9789750726439'),
(10, 6, 2, '9789750726439'),
(11, 10, 1, '9789750738609'),
(12, 10, 2, '9789750738609'),
(13, 11, 1, '9789754587173'),
(14, 6, 2, '9789754587173'),
(36, -1, 1, '9786052980811'),
(37, 1, 1, '9789755705859'),
(38, 1, 1, '9789756902165'),
(39, 2, 1, '9786053757818'),
(40, 4, 1, 'YMS'),
(41, 0, 1, '9789752430990'),
(42, 30, 1, 'Mustafa'),
(43, 2, 1, 'BTU'),
(44, 3, 2, 'VTYS'),
(45, 4, 2, 'VTYS2');



INSERT INTO `adminler` (`ID`, `KullaniciAdi`, `Sifre`, `KutuphaneID`) VALUES
(1, 'Admin1', 'Admin1', 1),
(2, 'Admin2', 'Admin2', 2);

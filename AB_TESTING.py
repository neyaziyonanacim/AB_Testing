#####################################################
# AB Testi ile Bidding Yöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.




#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç


import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# !pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp,shapiro,levene,ttest_ind,mannwhitneyu, \
    pearsonr,spearmanr,kendalltau,f_oneway,kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option("display.max_rows",10)
pd.set_option("display.max_columns",None)
pd.set_option("display.float_format",lambda x: "%.5f" % x)

#####################################################
# Proje Görevleri
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.




#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.


dfc=pd.read_excel("Datasets/ab_testing.xlsx", sheet_name="Control Group")
dfc.head()

dftest=pd.read_excel("Datasets/ab_testing.xlsx", sheet_name="Test Group")
dftest.head()

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.



# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

dfc["Bidding"]="max_bidding"

dftest["Bidding"]="aver_bidding"

df=pd.concat([dfc,dftest],ignore_index=True)
df.head()

#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.

#H0: M1=M2  iki yöntemın sonucları aynıdır, aralarında fark yoktur.
#H1: M1 !=M 2

# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz

df.groupby("Bidding").agg({"Purchase":"mean"})

#              Purchase
#Bidding
#aver_bidding 582.10610
#max_bidding  550.89406


#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################


# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz

#Normallık varsayımı - shapiro testi
#H0: Normal dağılım varsayımı sağlanmaktadır.
#H1: Normal dağılım varsayımı sağlanmamaktadır.
#p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ

test_stat,pvalue=shapiro(df.loc[df["Bidding"]=="max_bidding","Purchase"])
print("Test Stat =%.4f, p-value=%.4f" % (test_stat,pvalue))

#p-value=0.5891  teset stat=0.9773  , 1 yakın oldugu ıcın normal dagıldıgını gosterır.
# p degerı ıse test sonucunun ıstatıstıksel olarak anlamlı olup olmaıdgını belırler.
# p degerı test statın(0.9773) ne kadar anlamlı olup olmadıgını gosterır.
#demek kı ıstatısksel olarak anlamlılık var, cunku p > 0.05. normal dagılım oluyor.
#0.05 koselere yakın nokta, aykırı degerlere cok ızın vermıyo


test_stat,pvalue=shapiro(df.loc[df["Bidding"]=="aver_bidding","Purchase"])
print("Test Stat =%.4f, p-value=%.4f" % (test_stat,pvalue))

# p-value=0.1541

#olasılık grafıklerıne bak

# p value > 0.05. H0 reddedilmez. Normal dağılım varsayımı sağlanmaktadır.

# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz

#Varyans Homojenliği : levene testi
#H0: Varyanslar homojendir.
#H1: Varyanslar homojen Değildir.
#p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ

test_stat,pvalue=levene(df.loc[df["Bidding"]=="max_bidding","Purchase"],
                        df.loc[df["Bidding"]=="aver_bidding","Purchase"])
print("Test Stat =%.4f, p-value=%.4f" % (test_stat,pvalue))

#p-value=0.1083 . H0 reddedilmez.

# Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi (parametrik test)

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

test_stat,pvalue=ttest_ind(df.loc[df["Bidding"]=="max_bidding","Purchase"],
                        df.loc[df["Bidding"]=="aver_bidding","Purchase"],equal_var=True)

print("Test Stat =%.4f, p-value=%.4f" % (test_stat,pvalue))

#p-value=0.3493. Ho reddedilmez.

##############################################################
# GÖREV 4 : Sonuçların Analizi
##############################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

#Varsayımlar sağlandıgı ıcın bağımsız iki örneklem t testi (parametrik test) kullandım.

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

#AB test sonuçlarına göre her iki yöntem arasında istatistiki anlamda bir fark görülmemiştir.
# Gözlem sayısı artırılıp (>20) yenıden AB testı yapılabilir.
# Conversion rate ya da clıck through degsıckenlerı de goz onunde bulundurulabılır.

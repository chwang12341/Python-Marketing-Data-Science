## 載入數據
import pandas as pd
## 把顧客數據load進來
customer_data_df=pd.read_csv("data/Customer_Data.csv")


## 檢視訂單的狀態

## 查看訂單狀態有哪些屬性
customer_data_df['Order_form_status'].unique()
## 只保留訂單狀態(Order_form_status)為成功(success)的訂單
customer_data_df = customer_data_df.loc[customer_data_df['Order_form_status'] == 'success', :]
## 查看一下拿掉fail的訂單後，還剩幾筆資料
print('成立的訂單數量: ', len(customer_data_df))

## 查看一下數據資訊
customer_data_df.info()

## 根據顧客的id來分組，得到他們距離現在最近一次的購買時間點
Recency_df = customer_data_df.groupby('Client_Id')['Order_date'].max().reset_index()


## 獲取今天日期
import datetime
now = datetime.date.today()
## 計算距離今天幾天
Recency_df['Recency'] = (pd.to_datetime(now) - pd.to_datetime(Recency_df['Order_date'])).dt.days


## 增加一行日期標籤幫助我們接下來的計算，原本Order_date這個欄位會被我們當成是計算次數的欄位
customer_data_df['Date_Tag'] = customer_data_df['Order_date'].astype(str)
## 把同一天消費的訂單合併在一起，等等要忽略掉
dd_Frequency = customer_data_df.groupby(['Client_Id','Date_Tag'])['Order_date'].count().reset_index()
## 計算同一個客人在不同日期消費的次數
Frequency_df = dd_Frequency.groupby('Client_Id')['Order_date'].count().reset_index()
## 重新命名Order_date為Frequency
Frequency_df = Frequency_df.rename(columns={'Client_Id':'Client_Id','Order_date':'Frequency'})



## 根據顧客ID來計算個別顧客消費Fish品項的總額
Monetary_Fish= pd.DataFrame(customer_data_df.groupby('Client_Id')['Monetary_Fish'].sum().reset_index())
## 重新命名列名
Monetary_Fish = Monetary_Fish.rename(columns={'Client_Id':'Client_Id','Monetary_Fish':'Monetary_sum'})



## 合併 Monetary 與 Frequency
new_df = pd.merge(Monetary_Fish,Frequency_df, right_on="Client_Id", left_on="Client_Id")
## 計算個別顧客平均消費總額
new_df['Monetary'] = round(new_df['Monetary_sum'] / new_df['Frequency'])
## 合併最後一個欄位Recency
new_customer_data_df = pd.merge(new_df,Recency_df, right_on="Client_Id", left_on="Client_Id")
## 我們只需要RFM所需的數據
new_customer_data_df = new_customer_data_df[['Client_Id','Recency','Frequency', 'Monetary']]


## 幫Recency區分等級
new_customer_data_df['Recency_Level'] = pd.cut(new_customer_data_df['Recency'], bins=[0,40,80,120,160,1000000], labels=[5,4,3,2,1], right=False).astype(float)
## 幫Frequncy區分等級
new_customer_data_df['Frequency_Level'] = pd.cut(new_customer_data_df['Frequency'], bins=[1,2,3,4,5,10000000], labels=[1,2,3,4,5], right=False).astype(float)
## 幫Monetary區分等級
new_customer_data_df['Monetary_Level'] = pd.cut(new_customer_data_df['Monetary'], bins=[0,40,80,120,160,1000000000], labels=[1,2,3,4,5], right=False).astype(float)


## 幫Recency區分等級
new_customer_data_df['Recency_Level'] = pd.cut(new_customer_data_df['Recency'], bins=[0,40,80,120,160,1000000], labels=[5,4,3,2,1], right=False).astype(float)
## 幫Frequncy區分等級
new_customer_data_df['Frequency_Level'] = pd.cut(new_customer_data_df['Frequency'], bins=[1,2,3,4,5,10000000], labels=[1,2,3,4,5], right=False).astype(float)
## 幫Monetary區分等級
new_customer_data_df['Monetary_Level'] = pd.cut(new_customer_data_df['Monetary'], bins=[0,40,80,120,160,1000000000], labels=[1,2,3,4,5], right=False).astype(float)
## 顯示數據
new_customer_data_df

new_customer_data_df['New_Recency'] = (new_customer_data_df['Recency_Level'] > new_customer_data_df['Recency_Level'].mean())*1

new_customer_data_df['New_Frequency'] = (new_customer_data_df['Frequency_Level'] > new_customer_data_df['Frequency_Level'].mean())*1

new_customer_data_df['New_Monetary'] = (new_customer_data_df['Monetary_Level'] > new_customer_data_df['Monetary_Level'].mean())*1

## 顯示數據
new_customer_data_df

## 組合欄位
new_customer_data_df['Customer_Group'] = new_customer_data_df['New_Recency']*100+ new_customer_data_df['New_Frequency']*10 + new_customer_data_df['New_Monetary']
## 顯示數據
new_customer_data_df

## 組合欄位
new_customer_data_df['Customer_Group_value'] = new_customer_data_df['New_Recency']*100+ new_customer_data_df['New_Frequency']*10 + new_customer_data_df['New_Monetary']

## 定義分群標準
## 定義分群標準
def customer_group(value):
    if value == 111:
        label = '最重要的顧客'
    elif value == 110:
        label = '未來有消費潛力的顧客'
    elif value == 101:
        label = '消費頻率較低的顧客'
    elif value == 100:
        label = '新顧客'
    elif value == 11:
        label = '近期流失的重要顧客'
    elif value == 10:
        label = '普通顧客'
    elif value == 1:
        label = '流失掉的高消費顧客'
    elif value == 0:
        label = '不是我們的客群'
     
    return label

## 將Gender 和 Age 合併回去
gender_df = customer_data_df.groupby('Client_Id')['Gender'].max().reset_index()
Age_df = customer_data_df.groupby('Client_Id')['Age'].max().reset_index()
new_customer_data_df = pd.merge(new_customer_data_df, gender_df, right_on="Client_Id", left_on="Client_Id")
new_customer_data_df = pd.merge(new_customer_data_df, Age_df, right_on="Client_Id", left_on="Client_Id")
 
## 顧客分群
new_customer_data_df['RFM_顧客分群結果'] = new_customer_data_df['Customer_Group_value'].apply(customer_group)

## 將數據保存為csv檔
new_customer_data_df.to_csv("RFM_Model_Result.csv", encoding="utf_8_sig")

## 顯示數據
new_customer_data_df


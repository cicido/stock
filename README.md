# stock
1. 数据导出与预处理
load_k_data: 从招商证券采用数据导出方式得到当天或者过去几天的所有股票的数据。导到的数据包括沪深A股，板块指数
执行方式:
python load_k_data.py datadir sdate edate
datadir: 下载的股票数据目录，目录中每个文件表示一只股票或一个指数
sdate: 选取的开始日期(包括此日期,格式为yyyy-mm-dd)
edate: 选择的结束日期(同上)
例: python load_k_data.py /mnt/hgfs/Desktop/stock_data/ 2016-07-27 2016-11-21
之所以设置起始日期与结束日期，是可能某天忘了去导出数据，或者有一段时间忘了导出数据，这里能方便的进行控制。
此步完成后，会生成一个文件loaddata_$sdate_$edate

2. 数据分割
这一步主要应对内存不够采取的分文件处理方式，后续可能可以忽略这一步。
为减少每次处理量，将股票起始日期设置2014-01-01，从最后指标计算与招商证券界面显示结果来看，数据是一致的
采用如下脚本完成第一次的数据抽取
i.针对股票
while read file; do echo $file; awk -F'\t' '$3 > "2014-01-01"' /home/dxp/stock/statis/split_data/stock/$file > $file; done < <(ls /home/dxp/stock/statis/split_data/stock

ii.针对指数
while read file; do echo $file; awk -F'\t' '$3 > "2014-01-01"' /home/dxp/stock/statis/split_data/plate/$file > $file; done < <(ls /home/dxp/stock/statis/split_data/plate/)

其后每次的数据采用追加方式：
./split_today_data.sh ../load_k_data/data/loaddata_$sdate_$edata .
这一步主要保证一只股票的所有数据在同一个文件，从而可以单独进行计算

3. 指标计算

执行方式:

sh main.sh ../split_data/stock 0 stock
sh main.sh ../split_data/plate/ 0 plate

主要计算以下指标:
['MA','MACD','KDJ','RSI','GAIN','ORI','RESIST','VOL']
i. 其中GAIN是自定义的，主要用来计算涨跌贴幅及所处的范围:
-10.5 < x <= -9.5   -10
-9.5 < x <= -8.5     -9
...
-1.5 < x <= -0.5     -1
-0.5 < x <= 0.5      0
0.5 < x <= 1.5       1
...
8.5 < x <= 9.5       9
9.5 < x <= 10.5      10

ii. ORI是自定义的，主要用来合并数据用的，实际上并不是指标
iii. RESIST是自定义的，计算阻力用的。
iiiv. 其他指标都是根据招商证券的公式计算的


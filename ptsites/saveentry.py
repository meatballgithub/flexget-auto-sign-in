import json
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import re
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def save(entry):
    temp = {
        "site_name": entry["site_name"],
        "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
    }
    temp.update(entry["details"])
    temp = json.dumps(temp)
    with open("./data.json", "a") as f:
        f.write(temp)
        f.write("\n")


class ptAnalysis:
    def __init__(self):
        self.json = "data.json"
        self.csv = "data.csv"
        self.data = {}
        self.df = pd.DataFrame()
        self.oneday = 24 * 3600
        self.idx = -1

    def date2num(self, date):  # 字符串转时间戳
        temp = datetime.datetime.strptime(date, "%Y/%m/%d %H")
        return "{:.0f}".format(datetime.datetime.timestamp(temp))

    def num2date(self, num):  # 时间戳转 dattime 对象
        # return datetime.datetime.fromtimestamp(num)
        temp = datetime.datetime.fromtimestamp(num)
        temp = datetime.datetime.strftime(temp, "%Y/%m/%d %H")
        return datetime.datetime.strptime(temp, "%Y/%m/%d %H")

    def readvolume(self, up):
        if pd.isna(up):
            m = np.nan
        else:
            pattern1 = "^(-?\d+)(\.\d+)?"  # 浮点数
            pattern2 = "t[i]*b"  # t[i]b
            m = float(re.search(pattern1, up, flags=re.I).group())
            if re.search(pattern2, up, flags=re.I):
                m *= 1024
        return m

    def readdata(self):
        with open(self.json, "r") as f:
            for line in f:
                temp = json.loads(line)
                site_name = temp["site_name"]
                del temp["site_name"]
                # 忽略分钟,并转换成时间戳
                head, _, _ = temp["time"].partition(":")
                temp["time"] = self.date2num(head)
                if site_name in self.data.keys():
                    self.data[site_name]["time"].append(temp["time"])
                    self.data[site_name][site_name].append(temp["uploaded"])
                else:
                    self.data[site_name] = {
                        "time": [temp["time"]],
                        site_name: [temp["uploaded"]],
                    }
        # 转化成dataframe
        for key in self.data.keys():
            tempdf = pd.DataFrame(self.data[key])
            tempdf.drop_duplicates("time", inplace=True)
            if len(self.df.index) == 0:
                self.df = tempdf
            else:
                self.df = pd.merge(self.df, tempdf, on="time", how="outer")
        self.df.sort_values(by="time")
        try:
            df_origin = pd.read_csv(self.csv)
            df_origin.reset_index(True)
            self.df = pd.concat([df_origin, self.df], keys="time", sort=True)
        except:
            pass
        # 确保time存储的是数字，再去重复，排序
        self.df["time"] = pd.to_numeric(self.df["time"]).round(0).astype(int)
        self.df.drop_duplicates("time", inplace=True)
        self.df.sort_values(by="time")
        self.df.set_index("time")
        self.df.to_csv(self.csv, index=False)

    def plot(self, site_names, days=30):
        self.preprocess(days=days)
        n = len(site_names)
        if n == 1:
            figure, ax = plt.subplots()
            self.plotsingle(ax=ax, site_name=site_names[0])

        else:
            figure, ax = plt.subplots(
                n, 1, sharex=True, figsize=(24 / 2.54, n * 10 / 2.54)
            )
            plt.subplots_adjust(
                left=0.08, right=0.92, top=0.98, bottom=0.15 / n, hspace=0
            )
            for idx, site_name in enumerate(site_names):
                self.plotsingle(ax=ax[idx], site_name=site_name)
        plt.savefig("data.png", dpi=n * 20)

    def preprocess(self, days=30):
        # 原始数据
        self.t0_num = self.df["time"].to_numpy()
        self.t0_date = list(map(lambda x: self.num2date(x), self.df["time"].to_list()))

        # 画图时间段确定
        now = self.t0_date[-1]
        now = now.replace(hour=0, minute=0)
        if self.t0_date[-1] - self.t0_date[0] > datetime.timedelta(days=days):
            deltadays = days
        else:
            deltadays = (self.t0_date[-1] - self.t0_date[0]).days
        self.t1_date = [
            now - datetime.timedelta(days=deltadays - x - 1) for x in range(deltadays)
        ]
        self.t1_num = list(
            map(lambda x: self.date2num(x.strftime("%Y/%m/%d %H")), self.t1_date)
        )
        # 截取原始数据对应的画图段
        self.idx = -1
        while self.t0_date[self.idx] > self.t1_date[0]:
            self.idx -= 1

    def plotsingle(self, site_name=None, ax=None):
        y0 = self.df[site_name].map(lambda x: self.readvolume(x))
        try:
            y0 = y0.fillna(method="ffill", axis=0)
        except:
            y0 = y0.fillna(metho="backfill", axis=0)
        y0 = y0.to_numpy()
        # 计算每日增量
        y1 = np.interp(self.t1_num, self.t0_num, y0)
        if (self.t1_date[0] - self.t0_date[0]).days > 1:
            y2 = np.interp(self.t1_num - self.oneday, self.t0_num, y0)
        else:
            y2 = np.insert(y1[0:-1], 0, y1[0])
        dy = y1 - y2
        if y0[-1] > 1024:
            string1 = "{:.3f}TB".format(y0[-1] / 1024)
        else:
            string1 = "{:.2f}GB".format(y0[-1])
        sumup = y1[-1] - y1[0]
        if sumup > 1024:
            string2 = "{:.3f}TB".format(sumup / 1024)
        else:
            string2 = "{:.2f}GB".format(sumup)
        string = "{}\n upload:{}\nincrement:{}".format(site_name, string1, string2)

        if max(y0) > 1024:
            y0 = y0 / 1024
            ax.set_ylabel("upload/TB")
        else:
            ax.set_ylabel("upload/GB")
        ax.plot(
            self.t0_date[self.idx :], y0[self.idx :], marker="*", color="red",
        )

        ax1 = ax.twinx()
        ax1.text(
            s=string,
            x=self.t1_date[0],
            fontsize=16,
            y=max(dy) * 0.9,
            ha="left",
            va="top",
        )
        ax1.bar(
            self.t1_date,
            dy,
            width=0.6,
            color="grey",
            edgecolor="grey",
            align="center",
            alpha=0.5,
        )
        ax1.set_ylabel("increment/GB")
        for i in range(len(dy)):
            if dy[i] == 0:
                s = ""
            else:
                s = "{:.0f}".format(dy[i])
            xy = (self.t1_date[i], max(dy) * 0.1)
            ax1.annotate(s=s, xy=xy, color="blue", ha="center", va="baseline")
        ax.xaxis.set_major_formatter(mdate.DateFormatter("%m/%d"))
        for xtick in ax.get_xticklabels():
            xtick.set_rotation(45)
        ax.grid(True)


if __name__ == "__main__":
    pt = ptAnalysis()
    pt.readdata()
    pt.plot(
        site_names=[
            "hdhome",
            "springsunday",
            "hdsky",
            "open",
            "pterclub",
            "m-team",
            "eastgame",
        ]
    )
    print("done")

from sys import argv
from printOut import printOut
import codecs

# saldo = 0
# check = True
# logs = []
# storehouse = {}
# sourceLines = []
# count = 0


class Manager:
    def __init__(
        self,
        saldo=0,
        check=True,
        logs=[],
        storehouse={},
        sourceLines=[],
        count=0,
        actions={},
    ):
        self.saldo = saldo
        self.check = check
        self.logs = logs
        self.storehouse = storehouse
        self.sourceLines = sourceLines
        self.count = count
        self.actions = actions

    def assign(self, nazwa, lines):
        def fundwa(func):
            self.actions[nazwa] = func, lines

        return fundwa

    def exec(self):
        with open(argv[-2]) as source_file:
            while True:
                action = source_file.readline()
                if action == "":
                    break
                action = action.strip()
                if action not in self.actions:
                    continue
                lines = []
                for index in range(self.actions[action][1]):
                    lines.append(source_file.readline().strip())
                self.actions[action][0](self, *lines)

    def main(self):
        with open("in.txt") as sourceFile:
            for line in sourceFile:
                self.sourceLines.append(line)

        dataDest = codecs.open("out.txt", "w", "utf-8")
        switchCase = {"sprzedaż": self.sale_fun, "zakup": self.buy_fun}
        while self.check:
            action = self.sourceLines[self.count].strip()
            if action == "saldo":
                saldo = self.saldo_fun(
                    int(self.sourceLines[self.count + 1]),
                    self.sourceLines[self.count + 2].strip(),
                )
                self.count += 3
            elif action == "zakup" or action == "sprzedaż":
                switchCase[action](
                    self.sourceLines[self.count + 1].strip(),
                    int(self.sourceLines[self.count + 2]),
                    int(self.sourceLines[self.count + 3]),
                    dataDest,
                )
                self.count += 4
            elif action == "stop":
                if len(argv) == 1:
                    printOut(self.logs, dataDest)
                elif argv[1] == "saldo":
                    saldo = self.saldo_fun(int(argv[2]), argv[3])
                    dataDest.write(str(saldo))
                    break
                elif argv[1] == "zakup":
                    self.buy_fun(argv[2], int(argv[3]), int(argv[4]), dataDest)
                    if not self.check:
                        break
                    printOut(self.logs, dataDest)
                elif argv[1] == "sprzedaż":
                    self.sale_fun(
                        argv[2], int(argv[3]), int(argv[4]), dataDest
                    )
                    if not self.check:
                        break
                    printOut(self.logs, dataDest)
                elif argv[1] == "konto":
                    dataDest.write(str(saldo))
                    break
                elif argv[1] == "magazyn":
                    for name in argv[2:-2]:
                        if name in self.storehouse:
                            dataDest.write(
                                "{}: {}\n".format(name, self.storehouse[name])
                            )
                        else:
                            dataDest.write("{}: 0\n".format(name))
                elif argv[1] == "przegląd":
                    for index, log in enumerate(self.logs):
                        if index >= int(argv[2]) and index <= int(argv[3]):
                            if log == "stop":
                                dataDest.write("{}\n".format(log))
                                break
                            else:
                                for log_element in log:
                                    dataDest.write("{}\n".format(log_element))
                else:
                    printOut(self.logs, dataDest)
                self.logs.append("stop")
                dataDest.write(self.logs[-1])
                break
            else:
                dataDest.write(
                    "Błędna nazwa operacji. Podano {}".format(action)
                )
                break

    def saldo_fun(self, temp_saldo, comment):
        self.saldo += temp_saldo
        self.logs.append(("saldo", temp_saldo, comment))
        return self.saldo

    def buy_fun(self, product_id, unit_price, product_amount, dataDest):
        if self.saldo - unit_price * product_amount < 0:
            dataDest.write(
                "Błąd. Ujemne saldo po zakupie {} w ilości {}".format(
                    product_id, product_amount
                )
            )
            self.check = False
            return
        elif product_amount < 0:
            dataDest.write(
                "Błąd. Ujemna ilość zakupionego towaru {} w ilości {}".format(
                    product_id, product_amount
                )
            )
            self.check = False
            return
        elif unit_price * product_amount < 0:
            dataDest.write(
                "Błąd. Ujemna kwota zakupu {} w ilości {}".format(
                    product_id, product_amount
                )
            )
            self.check = False
            return
        self.logs.append(("zakup", product_id, unit_price, product_amount))
        if product_id in self.storehouse:
            self.storehouse[product_id] += product_amount
        else:
            self.storehouse[product_id] = product_amount
        self.saldo -= unit_price * product_amount

    def sale_fun(self, product_id, unit_price, product_amount, dataDest):
        if product_amount < 0:
            dataDest.write(
                "Błąd. Ujemna ilość zakupionego towaru {} w ilości {}".format(
                    product_id, product_amount
                )
            )
            self.check = False
            return
        elif unit_price * product_amount < 0:
            dataDest.write(
                "Błąd. Ujemna kwota zakupu {} w ilości {}".format(
                    product_id, product_amount
                )
            )
            self.check = False
            return
        self.logs.append(("sprzedaż", product_id, unit_price, product_amount))
        if product_id in self.storehouse:
            if self.storehouse[product_id] - product_amount < 0:
                self.check = False
                dataDest.write(
                    "Błąd. Brak niewystarczający stan produktu {} na magazynie".format(
                        product_id
                    )
                )
                return
            else:
                self.storehouse[product_id] -= product_amount
        else:
            dataDest.write(
                "Błąd. Brak produktu {} na magazynie".format(product_id)
            )
            self.check = False
            return
        self.saldo += unit_price * product_amount


manager = Manager()


# @manager.assign("saldo", 2)
# def saldo_funier(manager, temp_sum, comment):
#     manager.saldo += int(temp_sum)
#     print("Wartość salda: {}, {}".format(manager.saldo, comment))


# @manager.assign("sprzedaż", 3)
# def utylizacja(manager, product_id, unit_price, product_amount):
#     # Jeśli coś jest na magazynie odsyła wszystkie produkty poza egzemplarzem wystawowym
#     if product_id in manager.storehouse:
#         if manager.storehouse[product_id] > 1:
#             sent_back = manager.storehouse[product_id] - 1
#             manager.storehouse[product_id] -= sent_back
#             print("Odesłano {} produktu {}".format(sent_back, product_id))


# @manager.assign("zakup", 3)
# def buy_funier(manager, product_id, unit_price, product_amount):
#     print(
#         "Zakup produktu {}. Cena za sztukę {}".format(product_id, unit_price)
#     )


# manager.main()
# manager.exec()

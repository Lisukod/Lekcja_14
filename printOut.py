def printOut(logs, dataDest):
    for log in logs:
        if log == "stop":
            dataDest.write("{}\n".format(log))
        else:
            for log_element in log:
                dataDest.write("{}\n".format(log_element))

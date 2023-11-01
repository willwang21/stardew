import os
import xlrd

file = xlrd.open_workbook(os.path.join(os.getcwd(), 'sdv shipping.xls'))
crops_sheet = file.sheet_by_name('Crops')
plant_names = {x.value:i for i, x in enumerate(crops_sheet.col(0))}
col_headings = {x.value:i for i, x in enumerate(crops_sheet.row(0))}

GROWING = []
DAY_NUMBER = 1
CASH_ON_HAND = 20

class plant:
    def __init__(self, effective_revenue, days_first_harvest):
        self.effective_revenue = effective_revenue
        self.days_first_harvest = days_first_harvest
        self.age = 0
        GROWING.append(self)
        
    def get_older(self):
        self.age += 1
        
    def get_harvested(self):
        global CASH_ON_HAND, GROWING
        CASH_ON_HAND += self.effective_revenue
        GROWING = [plant for plant in GROWING if plant != self]
        
class multi_harvest_plant(plant):
    def __init__(self, effective_revenue, days_first_harvest, days_btwn_harvests):
        plant.__init__(self, effective_revenue, days_first_harvest)
        self.days_btwn_harvests = days_btwn_harvests
        self.had_first_harvest = False
    
    def get_harvested(self):
        global CASH_ON_HAND
        CASH_ON_HAND += self.effective_revenue
        self.age = 0
        if not self.had_first_harvest:
            self.had_first_harvest = True
        
def buy_plant(plant_name):
    global CASH_ON_HAND
    row_index = plant_names[plant_name]
    plant_info = crops_sheet.row(row_index)
    
    if CASH_ON_HAND - plant_info[col_headings['Cost (g)']].value < 0:
        print("You don't have enough money. :(")
        return None
    else:
        CASH_ON_HAND -= plant_info[col_headings['Cost (g)']].value
        
    if plant_info[col_headings['Single-use?']].value == 0:
        new_plant = multi_harvest_plant(
            plant_info[col_headings['Effective revenue (g)']].value,
            plant_info[col_headings['Days till first harvest']].value,
            plant_info[col_headings['Days between harvests']].value
        )
    else:
        new_plant = plant(
            plant_info[col_headings['Effective revenue (g)']].value,
            plant_info[col_headings['Days till first harvest']].value
        )
        
    return new_plant

def day_goes_by():
    global GROWING, DAY_NUMBER
    DAY_NUMBER += 1
    for plant in GROWING:
        plant.get_older()
        try:
            if not plant.had_first_harvest:
                if plant.age == plant.days_first_harvest:
                    plant.get_harvested()
            else:
                if plant.age == plant.days_btwn_harvests:
                    plant.get_harvested()
        except:
            if plant.age == plant.days_first_harvest:
                plant.get_harvested()

def season_change():
    global GROWING
    GROWING = []

def seasonROI(plant_name):
    global CASH_ON_HAND, DAY_NUMBER
    row_index = plant_names[plant_name]
    plant_info = crops_sheet.row(row_index)
    days_first_harvest = plant_info[col_headings['Days till first harvest']].value
    cycles_till_profitable = plant_info[col_headings['Cycles till profitable']].value
    days_btwn_harvests = plant_info[col_headings['Days between harvests']].value
    cost = plant_info[col_headings['Cost (g)']].value
    CASH_ON_HAND = cost
        
    while DAY_NUMBER < 28:
        day_goes_by()
        if DAY_NUMBER <= 28 - days_first_harvest - (cycles_till_profitable-1) * days_btwn_harvests:
            while CASH_ON_HAND >= cost:
                buy_plant(plant_name)
        
    return (CASH_ON_HAND / cost - 1) * 100

print(seasonROI('Parsnip'))
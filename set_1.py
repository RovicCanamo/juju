def savings(gross_pay, tax_rate, expenses):
    net_pay = gross_pay * (1 - tax_rate) 
    balance = net_pay - expenses
    return int(balance)

def material_waste(total_material, material_units, num_jobs, job_consumption):
    total_consumption = num_jobs * job_consumption
    remaining_material = total_material - total_consumption
    return str(remaining_material) + material_units

def interest(principal, rate, periods):
    interest_amount = principal * (rate * periods) 
    total_amount = principal + interest_amount
    return int(total_amount)
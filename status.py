def set_status(l_on, h_on, l_should_on, t_l, t_h):
    light_status = l_should_on
    heater_status = t_l or (h_on and (not t_l) and (not t_h))

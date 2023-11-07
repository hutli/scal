from math import acos, cos, cosh, log, sqrt


# Here be dragons - read https://gitlab.com/Erecco/a-study-on-quantum-travel-time to understand
def calc_z(v_max, a_1, a_2, d_tot):
    return (3 * (a_2 - a_1) ** 2 * (a_1 + a_2) ** 2 * d_tot) / (
        8 * a_1**3 * v_max**2
    ) - 1


def calc_d_c(v_max, a_1, a_2, d_tot):
    return d_tot - (4 * v_max**2 * (2 * a_1 + a_2)) / (3 * (a_1 + a_2) ** 2)


def calc_t_tot(v_max, a_1, a_2, d_tot, k):
    if calc_d_c(v_max, a_1, a_2, d_tot) < 0:
        z = calc_z(v_max, a_1, a_2, d_tot)
        if z > 1:
            return ((4 * a_1 * v_max) / (a_2**2 - a_1**2)) * (
                2 * cosh(1 / 3 * log(z - sqrt(z**2 - 1))) - 1
            ) + k
        acos_arg = (3 * (a_2 - a_1) ** 2 * (a_1 + a_2) ** 2 * d_tot) / (
            8 * a_1**3 * v_max**2
        ) - 1
        return (4 * a_1 * v_max) / (a_2**2 - a_1**2) * (
            2 * cos((1 / 3) * acos(acos_arg)) - 1
        ) + k
    else:
        return (
            (4 * v_max) / (a_1 + a_2)
            + d_tot / v_max
            - (4 * v_max * (2 * a_1 + a_2)) / (3 * (a_1 + a_2) ** 2)
            + k
        )


def sc_key(obj, key, second_key="Components"):
    return next(c for c in obj[second_key] if key in c.keys())[key]


def get_name(obj, show_size=False, alt=None):
    name = (
        sc_key(obj, "SAttachableComponentParams")["AttachDef"]["Localization"]["Name"]
        .replace("_SCItem", "")
        .rsplit("_", 1)[-1]
    )
    if "PLACEHOLDER" in name and alt:
        name = alt.replace("_SCItem", "").replace("_TEMP", "").split("_", 3)[-1]
    return name + (
        f'({sc_key(obj,"SAttachableComponentParams")["AttachDef"]["Size"]})'
        if show_size
        else ""
    )

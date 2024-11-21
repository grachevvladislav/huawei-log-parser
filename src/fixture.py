example = {
        "CTE0": {
            "R0": {
                "IOM0": ['P0', 'P1', 'P2', 'P3']
            },
            "R1": {
                "IOM0": ['P0', 'P1', 'P2', 'P3'],
                # "IOM1": ['P0', 'P1', 'P2', 'P3'],
            },
            "L0": {
                "IOM0": ['P0', 'P1', 'P2', 'P3']
            },
            "L1": {
                "IOM0": ['P0', 'P1', 'P2', 'P3']
            },
        #     "G1": ['P0', 'P1',],
        },
        # "CTE1": ['g']
    }

data_str = [
        "CTE0.R0.IOM0.P0->DAE000.A.PRI->DAE000.A.EXP->DAE001.A.PRI->DAE001.A.EXP->DAE002.A.PRI->DAE002.A.EXP->DAE003.A.PRI",
        "CTE0.R0.IOM0.P1->DAE010.A.PRI->DAE010.A.EXP->DAE011.A.PRI->DAE011.A.EXP->DAE012.A.PRI->DAE012.A.EXP->DAE013.A.PRI",
        "CTE0.R0.IOM0.P2->DAE020.A.PRI",
        "CTE0.R0.IOM0.P3",
        "CTE0.R1.IOM0.P0->DAE040.A.PRI->DAE040.A.EXP->DAE041.A.PRI->DAE041.A.EXP->DAE042.A.PRI->DAE042.A.EXP->DAE043.A.PRI",
        "CTE0.R1.IOM0.P1->DAE050.A.PRI->DAE050.A.EXP->DAE051.A.PRI->DAE051.A.EXP->DAE052.A.PRI->DAE052.A.EXP->DAE053.A.PRI",
        "CTE0.R1.IOM0.P2",
        "CTE0.R1.IOM0.P3",
        "CTE0.L1.IOM0.P0->DAE043.B.PRI->DAE043.B.EXP->DAE042.B.PRI->DAE042.B.EXP->DAE041.B.PRI->DAE041.B.EXP->DAE040.B.PRI",
        "CTE0.L1.IOM0.P1->DAE053.B.PRI->DAE053.B.EXP->DAE052.B.PRI->DAE052.B.EXP->DAE051.B.PRI->DAE051.B.EXP->DAE050.B.PRI",
        "CTE0.L1.IOM0.P2",
        "CTE0.L1.IOM0.P3",
        "CTE0.L0.IOM0.P0->DAE000.B.PRI->DAE000.B.EXP->DAE003.B.PRI->DAE003.B.EXP->DAE002.B.PRI->DAE002.B.EXP->DAE001.B.PRI",
        "CTE0.L0.IOM0.P1->DAE013.B.PRI->DAE013.B.EXP->DAE012.B.PRI->DAE012.B.EXP->DAE011.B.PRI->DAE011.B.EXP->DAE010.B.PRI",
        "CTE0.L0.IOM0.P2->DAE020.B.PRI",
        "CTE0.L0.IOM0.P3",
    ]
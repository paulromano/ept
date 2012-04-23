#!/usr/bin/env python

"""
Vision processing.
"""

from __future__ import division, print_function

from fileIO import fileReSeek

fissionProducts = ['H3','Co72','Co73','Co74','Co75','Ni72','Ni73','Ni74','Ni75',
                   'Ni76','Ni77','Ni78','Cu72','Cu73','Cu74','Cu75','Cu76',
                   'Cu77','Cu78','Cu79','Cu80','Cu81','Zn72','Zn73','Zn74',
                   'Zn75','Zn76','Zn77','Zn78','Zn79','Zn80','Zn81','Zn82',
                   'Zn83','Ga72','Ga73','Ga74','Ga75','Ga76','Ga77','Ga78',
                   'Ga79','Ga80','Ga81','Ga82','Ga83','Ga84','Ga85','Ge72',
                   'Ge73','Ge73M','Ge74','Ge75','Ge75M','Ge76','Ge77','Ge77M',
                   'Ge78','Ge79','Ge80','Ge81','Ge82','Ge83','Ge84','Ge85',
                   'Ge86','Ge87','Ge88','As75','As76','As77','As78','As78M',
                   'As79','As80','As81','As82','As82M','As83','As84','As85',
                   'As86','As87','As88','As89','As90','Se76','Se77','Se77M',
                   'Se78','Se79','Se79M','Se80','Se81','Se81M','Se82','Se83',
                   'Se83M','Se84','Se85','Se85M','Se86','Se87','Se88','Se89',
                   'Se90','Se91','Se92','Se93','Br79','Br79M','Br80','Br80M',
                   'Br81','Br82','Br82M','Br83','Br84','Br84M','Br85','Br86',
                   'Br86M','Br87','Br88','Br89','Br90','Br91','Br92','Br93',
                   'Br94','Br95','Br96','Kr80','Kr81','Kr81M','Kr82','Kr83',
                   'Kr83M','Kr84','Kr85','Kr85M','Kr86','Kr87','Kr88','Kr89',
                   'Kr90','Kr91','Kr92','Kr93','Kr94','Kr95','Kr96','Kr97',
                   'Kr98','Rb85','Rb86','Rb86M','Rb87','Rb88','Rb89','Rb90',
                   'Rb90M','Rb91','Rb92','Rb93','Rb94','Rb95','Rb96','Rb97',
                   'Rb98','Rb99','Rb100','Rb101','Sr86','Sr87','Sr87M','Sr88',
                   'Sr89','Sr90','Sr91','Sr92','Sr93','Sr94','Sr95','Sr96',
                   'Sr97','Sr98','Sr99','Sr100','Sr101','Sr102','Sr103','Sr104',
                   'Y89','Y89M','Y90','Y90M','Y91','Y91M','Y92','Y93','Y93M',
                   'Y94','Y95','Y96','Y96M','Y97','Y97M','Y98','Y98M','Y99',
                   'Y100','Y101','Y102','Y103','Y104','Y105','Y106','Y107',
                   'Zr90','Zr90M','Zr91','Zr92','Zr93','Zr94','Zr95','Zr96',
                   'Zr97','Zr98','Zr99','Zr100','Zr101','Zr102','Zr103','Zr104',
                   'Zr105','Zr106','Zr107','Zr108','Zr109','Nb93','Nb93M',
                   'Nb94','Nb94M','Nb95','Nb95M','Nb96','Nb97','Nb97M','Nb98',
                   'Nb98M','Nb99','Nb99M','Nb100','Nb100M','Nb101','Nb102',
                   'Nb103','Nb104','Nb105','Nb106','Nb107','Nb108','Nb109',
                   'Nb110','Nb111','Nb112','Mo95','Mo96','Mo97','Mo98','Mo99',
                   'Mo100','Mo101','Mo102','Mo103','Mo104','Mo105','Mo106',
                   'Mo107','Mo108','Mo109','Mo110','Mo111','Mo112','Mo113',
                   'Mo114','Mo115','Tc99','Tc99M','Tc100','Tc101','Tc102',
                   'Tc102M','Tc103','Tc104','Tc105','Tc106','Tc107','Tc108',
                   'Tc109','Tc110','Tc111','Tc112','Tc113','Tc114','Tc115',
                   'Tc116','Tc117','Tc118','Ru99','Ru100','Ru101','Ru102',
                   'Ru103','Ru104','Ru105','Ru106','Ru107','Ru108','Ru109',
                   'Ru110','Ru111','Ru112','Ru113','Ru114','Ru115','Ru116',
                   'Ru117','Ru118','Ru119','Ru120','Rh103','Rh103M','Rh104',
                   'Rh104M','Rh105','Rh105M','Rh106','Rh106M','Rh107','Rh108',
                   'Rh108M','Rh109','Rh109M','Rh110','Rh110M','Rh111','Rh112',
                   'Rh113','Rh114','Rh115','Rh116','Rh117','Rh118','Rh119',
                   'Rh120','Rh121','Rh122','Rh123','Pd104','Pd105','Pd106',
                   'Pd107','Pd107M','Pd108','Pd109','Pd109M','Pd110','Pd111',
                   'Pd111M','Pd112','Pd113','Pd114','Pd115','Pd116','Pd117',
                   'Pd118','Pd119','Pd120','Pd121','Pd122','Pd123','Pd124',
                   'Pd125','Pd126','Ag107','Ag108','Ag108M','Ag109','Ag109M',
                   'Ag110','Ag110M','Ag111','Ag111M','Ag112','Ag113','Ag113M',
                   'Ag114','Ag115','Ag115M','Ag116','Ag116M','Ag117','Ag117M',
                   'Ag118','Ag118M','Ag119','Ag120','Ag121','Ag122','Ag123',
                   'Ag124','Ag125','Ag126','Ag127','Ag128','Cd106','Cd108',
                   'Cd109','Cd110','Cd111','Cd111M','Cd112','Cd113','Cd113M',
                   'Cd114','Cd115','Cd115M','Cd116','Cd117','Cd117M','Cd118',
                   'Cd119','Cd119M','Cd120','Cd121','Cd122','Cd123','Cd124',
                   'Cd125','Cd126','Cd127','Cd128','Cd129','Cd130','Cd131',
                   'Cd132','In113','In113M','In114','In114M','In115','In115M',
                   'In116','In116M','In117','In117M','In118','In118M','In119',
                   'In119M','In120','In120M','In121','In121M','In122','In122M',
                   'In123','In123M','In124','In125','In125M','In126','In127',
                   'In127M','In128','In129','In130','In131','In132','In133',
                   'In134','Sn112','Sn114','Sn115','Sn116','Sn117','Sn117M',
                   'Sn118','Sn119','Sn119M','Sn120','Sn121','Sn121M','Sn122',
                   'Sn123','Sn123M','Sn124','Sn125','Sn125M','Sn126','Sn127',
                   'Sn127M','Sn128','Sn129','Sn129M','Sn130','Sn131','Sn132',
                   'Sn133','Sn134','Sn135','Sn136','Sb121','Sb122','Sb122M',
                   'Sb123','Sb124','Sb124M','Sb125','Sb126','Sb126M','Sb127',
                   'Sb128','Sb128M','Sb129','Sb130','Sb130M','Sb131','Sb132',
                   'Sb132M','Sb133','Sb134','Sb134M','Sb135','Sb136','Sb137',
                   'Sb138','Sb139','Te122','Te123','Te123M','Te124','Te125',
                   'Te125M','Te126','Te127','Te127M','Te128','Te129','Te129M',
                   'Te130','Te131','Te131M','Te132','Te133','Te133M','Te134',
                   'Te135','Te136','Te137','Te138','Te139','Te140','Te141',
                   'Te142','I127','I128','I129','I130','I130M','I131','I132',
                   'I133','I133M','I134','I134M','I135','I136','I136M','I137',
                   'I138','I139','I140','I141','I142','I143','I144','I145',
                   'Xe128','Xe129','Xe129M','Xe130','Xe131','Xe131M','Xe132',
                   'Xe133','Xe133M','Xe134','Xe134M','Xe135','Xe135M','Xe136',
                   'Xe137','Xe138','Xe139','Xe140','Xe141','Xe142','Xe143',
                   'Xe144','Xe145','Xe146','Xe147','Cs133','Cs134','Cs134M',
                   'Cs135','Cs135M','Cs136','Cs137','Cs138','Cs138M','Cs139',
                   'Cs140','Cs141','Cs142','Cs143','Cs144','Cs145','Cs146',
                   'Cs147','Cs148','Cs149','Cs150','Ba134','Ba135','Ba135M',
                   'Ba136','Ba136M','Ba137','Ba137M','Ba138','Ba139','Ba140',
                   'Ba141','Ba142','Ba143','Ba144','Ba145','Ba146','Ba147',
                   'Ba148','Ba149','Ba150','Ba151','Ba152','La138','La139',
                   'La140','La141','La142','La143','La144','La145','La146',
                   'La147','La148','La149','La150','La151','La152','La153',
                   'La154','La155','Ce140','Ce141','Ce142','Ce143','Ce144',
                   'Ce145','Ce146','Ce147','Ce148','Ce149','Ce150','Ce151',
                   'Ce152','Ce153','Ce154','Ce155','Ce156','Ce157','Pr141',
                   'Pr142','Pr142M','Pr143','Pr144','Pr144M','Pr145','Pr146',
                   'Pr147','Pr148','Pr149','Pr150','Pr151','Pr152','Pr153',
                   'Pr154','Pr155','Pr156','Pr157','Pr158','Pr159','Nd142',
                   'Nd143','Nd144','Nd145','Nd146','Nd147','Nd148','Nd149',
                   'Nd150','Nd151','Nd152','Nd153','Nd154','Nd155','Nd156',
                   'Nd157','Nd158','Nd159','Nd160','Nd161','Pm147','Pm148',
                   'Pm148M','Pm149','Pm150','Pm151','Pm152','Pm152M','Pm153',
                   'Pm154','Pm154M','Pm155','Pm156','Pm157','Pm158','Pm159',
                   'Pm160','Pm161','Pm162','Sm147','Sm148','Sm149','Sm150',
                   'Sm151','Sm152','Sm153','Sm154','Sm155','Sm156','Sm157',
                   'Sm158','Sm159','Sm160','Sm161','Sm162','Sm163','Sm164',
                   'Sm165','Eu151','Eu152','Eu152M','Eu153','Eu154','Eu155',
                   'Eu156','Eu157','Eu158','Eu159','Eu160','Eu161','Eu162',
                   'Eu163','Eu164','Eu165','Gd152','Gd153','Gd154','Gd155',
                   'Gd156','Gd157','Gd158','Gd159','Gd160','Gd161','Gd162',
                   'Gd163','Gd164','Gd165','Tb159','Tb160','Tb161','Tb162',
                   'Tb162M','Tb163','Tb163M','Tb164','Tb165','Dy160','Dy161',
                   'Dy162','Dy163','Dy164','Dy165','Dy165M','Dy166','Ho165',
                   'Ho166','Ho166M','Er166','Er167','Er167M']

lanthanides = ['La138','La139','La140','La141','La142','La143','La144','La145',
               'La146','La147','La148','La149','La150','La151','La152','La153',
               'La154','La155','Ce140','Ce141','Ce142','Ce143','Ce145','Ce146',
               'Ce147','Ce148','Ce149','Ce150','Ce151','Ce152','Ce153','Ce154',
               'Ce155','Ce156','Ce157','Pr141','Pr142','Pr142M','Pr143','Pr145',
               'Pr146','Pr147','Pr148','Pr149','Pr150','Pr151','Pr152','Pr153',
               'Pr154','Pr155','Pr156','Pr157','Pr158','Pr159','Nd142','Nd143',
               'Nd144','Nd145','Nd146','Nd147','Nd148','Nd149','Nd150','Nd151',
               'Nd152','Nd153','Nd154','Nd155','Nd156','Nd157','Nd158','Nd159',
               'Nd160','Nd161','Pm148','Pm148M','Pm149','Pm150','Pm151','Pm152',
               'Pm152M','Pm153','Pm154','Pm154M','Pm155','Pm156','Pm157',
               'Pm158','Pm159','Pm160','Pm161','Pm162','Sm148','Sm149','Sm150',
               'Sm152','Sm153','Sm154','Sm155','Sm156','Sm157','Sm158','Sm159',
               'Sm160','Sm161','Sm162','Sm163','Sm164','Sm165','Eu151','Eu152',
               'Eu152M','Eu153','Eu156','Eu157','Eu158','Eu159','Eu160','Eu161',
               'Eu162','Eu163','Eu164','Eu165','Gd152','Gd153','Gd154','Gd155',
               'Gd156','Gd157','Gd158','Gd159','Gd160','Gd161','Gd162','Gd163',
               'Gd164','Gd165','Tb159','Tb160','Tb161','Tb162','Tb162M','Tb163',
               'Tb163M','Tb164','Tb165','Dy160','Dy161','Dy162','Dy163','Dy164',
               'Dy165','Dy165M','Dy166','Ho165','Ho166','Er166','Er167','Er167M']
             
def writeInput(filename, charge, discharge):
    """
    Formats data from a charge Material and a discharge Material into a form
    suitable for VISION input. Two files are written out:

    vision.txt  -- list of isotopes for VISION
    summary.txt -- summary of equations for calculating total mass

    The equations for total masses are based on the list of isotopes in
    isoprocess.txt.
    """
    
    #extrapath = "Rebuscode/postprocess/"

    visionFile = open(filename,"w")
    visionFile.write("ISOTOPE     CHARGE      DISCHARGE\n")
    summaryFile = open("summary.txt","w")

    # Open Output/summary.txt
    
    isoFile = open("isoprocess.txt", "r")
    m = fileReSeek(isoFile, "^NOISOTOPES\s+(\d+).*")
    n_total = eval(m.groups()[0])

    for i in range(1,n_total+1):
        isoFile.seek(0)

        # Read isotopes
        m = fileReSeek(isoFile, "^ISOTOPE{0:03}\s(\d+)\s(.*)".format(i))
        if not m:
            print("ISOTOPE{0} not found!".format(i))
            return 1
        n_isotopes = eval(m.groups()[0])
        isotopes = m.groups()[1].split()

        # Determine name for grouped isotope
        if len(isotopes) > n_isotopes:
            name = isotopes[-1]
        else:
            name = isotopes[0]

        # Special treatment for FPs and Lanthanides
        if isotopes[0] == "FP":
            isotopes = fissionProducts
        elif isotopes[0] == "LA":
            isotopes = lanthanides

        # Determine weighting coefficients
        m = fileReSeek(isoFile, "^WEIGHTS{0:03}(.*)/.*".format(i))
        if m:
            weights = [eval(j) for j in m.groups()[0].split()]
        else:
            weights = [1 for isotope in isotopes]

        # Print summary information
        if n_isotopes >= 2 and n_isotopes < 50:
            equation = name + " = "
            for index in range(n_isotopes):
                if index != 0:
                    equation += " + "
                if weights[index] != 1:
                    equation += "{0!s} * ".format(weights[index])
                equation += isotopes[index]
            summaryFile.write(equation + "\n")

        # Calculate charge and discharge masses
        chargeMass = 0.0
        dischargeMass = 0.0
        for index, isotope in enumerate(isotopes):
            # If isotope is in charge material, add its mass
            iso = charge.find(isotope)
            if iso:
                chargeMass += iso.mass*weights[index]
            # If isotope is in discharge material, add its mass
            iso = discharge.find(isotope)
            if iso:
                dischargeMass += iso.mass*weights[index]

        # Write masses to visionFile
        if isotopes:
            visionFile.write("{0:12}{1:<12.4E}{2:<12.4E}\n".format(
                    name, chargeMass, dischargeMass))

    isoFile.close()
    visionFile.close()
    summaryFile.close()

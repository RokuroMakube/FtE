import os
from xml.dom import minidom
import datetime
import xlsxwriter
import win32com.client
from base64 import b64decode

def NonVuoto(x): #FUNZIONE PER VERIFICARE CHE UNA VOCE NON SIA VUOTA
    return len(x) != 0
def Vuoto(x): #FUNZIONE PER VERIFICARE CHE UNA VOCE SIA VUOTA
    return len(x) == 0
def DataItaliana(x):
    lista = list(x.split("-"))
    data_finale = lista[2] + "-" + lista[1] + "-" + lista[0]
    return data_finale


program_path = os.getcwd() #PATH DELLA CARTELLA CON IL PROGRAMMA
fe_path = program_path + "/Fatture Elettroniche" #PATH DELLA CARTELLA CON LE FATTURE ELETTRONICHE
openssl_path = program_path + "\OpenSSL" #PATH DELLA CARTELLA CON OPENSSL
os.system('setx PATH "%PATH%;' + openssl_path + '" /M')
fatture_convertite_path = program_path + "/Fatture Excel"

file = os.listdir(fe_path) #LISTA CON TUTTI I NOME DEI FILE DELLA CARTELLA

for x in range(len(file)):
    full_file_path = os.path.abspath(os.path.join(program_path, file[x]))
    if ".p7m" in file[x]:
        os.chdir(fe_path)
        os.system('openssl smime -verify -noverify -in ' + file[x] + ' -inform DER -out ' + str(x) + '.xml')
        os.remove(file[x])

os.chdir(program_path)
file = os.listdir(fe_path)

for i in range(len(file)): #LOOP PER TUTTI I FILE DENTRO LA CARTELLA

    full_file_path = os.path.abspath(os.path.join('Fatture Elettroniche', file[i]))

    xmldoc = minidom.parse(full_file_path) #ALLOCA TUTTI I DATI DEL FILE XML NELLA MEMORIA

    cedente_prestatore = xmldoc.getElementsByTagName('CedentePrestatore')

    nome_azienda = (cedente_prestatore[0].getElementsByTagName('Denominazione')[0].firstChild.data)#.encode("utf-8")<- I VARI ENCODE SERVONO IN PYTHON2, IN PYTHON3 NO IN QUANTO LE STRINGHE
                                                                                            #IN PYTHON3 SONO IN UNICODE, MENTRE IN PYTHON2 LE DEVI CONVERTIRE

    dati_documento =  xmldoc.getElementsByTagName('DatiGeneraliDocumento')
    data_fattura = dati_documento[0].getElementsByTagName('Data')[0].firstChild.data
    data_fattura_italiana = DataItaliana(data_fattura)

    os.chdir(fatture_convertite_path)
    nome_excel = nome_azienda + ", " + data_fattura_italiana + ", " + str(i+1)
    outExcel = xlsxwriter.Workbook(nome_excel + ".xlsx") #CREA FILE EXCEL NELLA DIRECTORY
    outSheet = outExcel.add_worksheet() #CREA UNA SHEET NEL FILE EXCEL DOVE SCRIVERE LA ROBA

    bold = outExcel.add_format({'bold': True}) #PERSONALIZZATORI DI CARATTERI/CASELLE
    bold_centrato = outExcel.add_format()
    bold_centrato.set_align('center')
    bold_centrato.set_bold()
    centrato= outExcel.add_format()
    centrato.set_align('center')
    giallo = outExcel.add_format()
    giallo.set_bg_color('yellow')
    grigio = outExcel.add_format()
    grigio.set_bg_color('#D3D3D3')
    grigio_bold = outExcel.add_format()
    grigio_bold.set_bold()
    grigio_bold.set_bg_color('#D3D3D3')
    grigio_centrato = outExcel.add_format()
    grigio_centrato.set_bg_color('#D3D3D3')
    grigio_centrato.set_align('center')
    grigio_centrato_bold = outExcel.add_format()
    grigio_centrato_bold.set_bold()
    grigio_centrato_bold.set_bg_color('#D3D3D3')
    grigio_centrato_bold.set_align('center')
    bold_14 = outExcel.add_format()
    bold_14.set_font_size(14)
    bold_14.set_bold()

    outSheet.write_string("A1", nome_azienda + ", " + data_fattura_italiana, bold_14)

    id_fiscale_IVA = cedente_prestatore[0].getElementsByTagName('IdFiscaleIVA')
    partita_iva = id_fiscale_IVA[0].getElementsByTagName('IdCodice')[0].firstChild.data
    outSheet.write_string("A2", "Partita IVA: " + partita_iva, bold)
    codice_fiscale_grezzo = cedente_prestatore[0].getElementsByTagName('CodiceFiscale')
    if NonVuoto(codice_fiscale_grezzo):
        codice_fiscale = codice_fiscale_grezzo[0].firstChild.data
        outSheet.write_string("A3", "Codice Fiscale: " + codice_fiscale, bold)
    numero_fattura = dati_documento[0].getElementsByTagName('Numero')[0].firstChild.data
    outSheet.write_string("A4", "FATTURA numero: " + numero_fattura + ", del " + data_fattura_italiana, bold)

    indirizzo_emittente = cedente_prestatore[0].getElementsByTagName('Indirizzo')[0].firstChild.data
    comune_emittente = cedente_prestatore[0].getElementsByTagName('Comune')[0].firstChild.data
    provincia_emittente_grezza = cedente_prestatore[0].getElementsByTagName('Provincia')
    if NonVuoto(provincia_emittente_grezza):
        provincia_emittente = provincia_emittente_grezza[0].firstChild.data
        outSheet.write_string("A6", indirizzo_emittente + " " + comune_emittente + "," + provincia_emittente)
    else:
        outSheet.write_string("A6", indirizzo_emittente + "," + comune_emittente)
    dati_trasporto = xmldoc.getElementsByTagName('DatiDDT')
    if NonVuoto(dati_trasporto):
        numero_trasporto = dati_trasporto[0].getElementsByTagName('NumeroDDT')[0].firstChild.data
        data_DDT = dati_trasporto[0].getElementsByTagName('DataDDT')[0].firstChild.data
        outSheet.write_string("A5", "DDT: " + numero_trasporto + ", del " + data_DDT, bold)
    email_grezza = xmldoc.getElementsByTagName('Email')
    if NonVuoto(email_grezza):
        email = email_grezza[0].firstChild.data
        outSheet.write_string("A7", "e-mail: " + email)
    telefono_grezzo = cedente_prestatore[0].getElementsByTagName('Telefono')
    if NonVuoto(telefono_grezzo):
        telefono = telefono_grezzo[0].firstChild.data
        outSheet.write_string("A8", "Telefono: " + telefono)
    indirizzo_emittente = cedente_prestatore[0].getElementsByTagName('Indirizzo')[0].firstChild.data
    comune_emittente = cedente_prestatore[0].getElementsByTagName('Comune')[0].firstChild.data
    provincia_emittente_grezza = cedente_prestatore[0].getElementsByTagName('Provincia')
    if NonVuoto(provincia_emittente_grezza):
        provincia_emittente = provincia_emittente_grezza[0].firstChild.data
        outSheet.write_string("A6", indirizzo_emittente + " " + comune_emittente + "," + provincia_emittente)
    else:
        outSheet.write_string("A6", indirizzo_emittente + "," + comune_emittente)

    outSheet.write_string("D1", "Dati Cliente")
    cessionario_committente = xmldoc.getElementsByTagName('CessionarioCommittente')
    denominazione_cliente_grezza = cessionario_committente[0].getElementsByTagName('Denominazione')
    if NonVuoto(denominazione_cliente_grezza):
        denominazione_cliente = denominazione_cliente_grezza[0].firstChild.data
        outSheet.write_string("D2", denominazione_cliente, bold)
    else:
        nome_cliente = cessionario_committente[0].getElementsByTagName('Nome')[0].firstChild.data
        cognome_cliente = cessionario_committente[0].getElementsByTagName('Cognome')[0].firstChild.data
        outSheet.write_string("D2", nome_cliente + " " + cognome_cliente, bold)
    id_fiscale_IVA_cliente = cessionario_committente[0].getElementsByTagName('IdFiscaleIVA')
    partita_iva_cliente = id_fiscale_IVA[0].getElementsByTagName('IdCodice')[0].firstChild.data
    outSheet.write_string("D3", "Partita IVA: " + partita_iva_cliente, bold)
    codice_fiscale_grezzo_cliente = cessionario_committente[0].getElementsByTagName('CodiceFiscale')
    if NonVuoto(codice_fiscale_grezzo_cliente):
        codice_fiscale_cliente = codice_fiscale_grezzo_cliente[0].firstChild.data
        outSheet.write_string("D4", "Codice Fiscale: " + codice_fiscale_cliente, bold)
    indirizzo_cliente = cessionario_committente[0].getElementsByTagName('Indirizzo')[0].firstChild.data
    comune_cliente = cessionario_committente[0].getElementsByTagName('Comune')[0].firstChild.data
    provincia_cliente_grezza = cessionario_committente[0].getElementsByTagName('Provincia')
    if NonVuoto(provincia_cliente_grezza):
        provincia_cliente = provincia_cliente_grezza[0].firstChild.data
        outSheet.write_string("D5", indirizzo_cliente + " " + comune_cliente + "," + provincia_cliente)
    else:
        outSheet.write_string("D5", indirizzo_cliente + "," + comune_cliente)

    dati_trasporto = xmldoc.getElementsByTagName('DatiDDT')
    if NonVuoto(dati_trasporto):
        numero_trasporto = dati_trasporto[0].getElementsByTagName('NumeroDDT')[0].firstChild.data
        data_DDT = dati_trasporto[0].getElementsByTagName('DataDDT')[0].firstChild.data
        outSheet.write_string("A5", "DDT: " + numero_trasporto + ", del " + data_DDT, bold)
    email_grezza = xmldoc.getElementsByTagName('Email')
    if NonVuoto(email_grezza):
        email = email_grezza[0].firstChild.data
        outSheet.write_string("A7", "e-mail: " + email)
    telefono_grezzo = cedente_prestatore[0].getElementsByTagName('Telefono')
    if NonVuoto(telefono_grezzo):
        telefono = telefono_grezzo[0].firstChild.data
        outSheet.write_string("A8", "Telefono: " + telefono)

    outSheet.write_string("A10", "Prodotto", centrato)

    #outSheet.write_string("B1", "Data Fattura", centrato)
    #outSheet.write_string("B2", data_fattura_italiana, bold_centrato)
    outSheet.write_string("B3", "Data Scadenza", centrato)
    data_scadenza_grezza = xmldoc.getElementsByTagName('DataScadenzaPagamento')
    if NonVuoto(data_scadenza_grezza):
        data_scadenza = data_scadenza_grezza[0].firstChild.data
        data_scadenza_italiana = DataItaliana(data_scadenza)
        outSheet.write("B4", data_scadenza_italiana, bold_centrato)

    CAP_emittente = cedente_prestatore[0].getElementsByTagName('CAP')[0].firstChild.data
    outSheet.write_string("B6", "CAP: " + CAP_emittente)
    outSheet.write_string("B10", "Quantita'", centrato)

    outSheet.write_string("C10", "PrezzoUnitario", centrato)

    #outSheet.write_string("xx", "AliquotaIVA")

    outSheet.set_column(0, 0, 44) #MODIFICA COLONNA DOVE HAI: PRIMA E ULTIMA COLONNA CHE VUOI MODIFICARE, LARGHEZZA DELLA COLONNA
    outSheet.set_column(1, 1, 12.7)
    outSheet.set_column(2, 2, 12.9)
    outSheet.set_column(3, 3, 13)
    outSheet.set_column(4, 4, 9.4)
    outSheet.set_column(5, 5, 11)
    outSheet.set_column(6, 6, 13)
    outSheet.set_column(7, 7, 3)

    pezzi = xmldoc.getElementsByTagName('DettaglioLinee')
    lordo_totale = 0
    somma_lordi_totali = 0
    sconto_totale = 0
    totale_scontato = 0
    stringa_tot = ""
    for j in range(len(pezzi)):

        if ((j+10)%2) == 0:
            #outSheet.set_row(j+10, 15, grigio) #PER COLORARE DI GRIGIO TUTTA LA RIGA ALL'INFITO
            cell_format_bold = outExcel.add_format()
            cell_format_bold.set_bold()
            cell_format_bold.set_bg_color('#D3D3D3')
            cell_format_bold.set_align('center')
            cell_format = outExcel.add_format()
            cell_format.set_bg_color('#D3D3D3')
            cell_format.set_align('center')
            formato_prodotto = grigio_bold
        else:
            cell_format = outExcel.add_format()
            cell_format.set_bg_color('white')
            cell_format.set_align('center')
            cell_format_bold = outExcel.add_format()
            cell_format_bold.set_bold()
            cell_format_bold.set_align('center')
            formato_prodotto = outExcel.add_format()
            formato_prodotto.set_bold()

        descrezione_grezza = pezzi[j].getElementsByTagName('Descrizione')
        descrizione = (descrezione_grezza[0].firstChild.data)#.encode("utf-8") VEDI RIGA 37

        if "Sconto" in descrizione or "Sconti" in descrizione or "SCONTO" in descrizione or "sconto" in descrizione:
            sconto_unitario_grezzo = pezzi[j].getElementsByTagName('PrezzoUnitario')
            sconto_unitario = float(sconto_unitario_grezzo[0].firstChild.data)
            if j==0 or j==(len(pezzi)-1) and "Cassa" in descrizione or "CASSA" in descrizione or "cassa" in descrizione:
                outSheet.write_string(j+10, 0, descrizione, formato_prodotto)
                outSheet.write(j+10, 4, sconto_unitario, cell_format_bold)
            else:
                outSheet.write(j+9, 4, sconto_unitario, grigio_centrato)
            sconto_totale += sconto_unitario

        else:
            outSheet.write_string(j+10, 0, descrizione, formato_prodotto)

            prezzi_unitari_grezzi = pezzi[j].getElementsByTagName('PrezzoUnitario')
            prezzi_unitari = float(prezzi_unitari_grezzi[0].firstChild.data)
            outSheet.write(j+10, 2, prezzi_unitari, cell_format)

            quantita_grezza = pezzi[j].getElementsByTagName('Quantita')
            if NonVuoto(quantita_grezza):
                quantita = int(float(quantita_grezza[0].firstChild.data))
                outSheet.write(j+10, 1, quantita, cell_format_bold)
                lordo_totale = prezzi_unitari*quantita
                outSheet.write(j+10, 3, lordo_totale, cell_format)
                somma_lordi_totali += lordo_totale
                #outSheet.write("D" + str(j+14), somma_lordi_totali, bold_centrato)

                #iva_prodotto = pezzi[j].getElementsByTagName('AliquotaIVA')[0].firstChild.data #IVA DEI PRODOTTI, COMMENTATA PERCHE' NON MI SERVIVA MA L'HO AGGIUNTA COMUNQUE
                #outSheet.write_string(j+7, 7, iva_prodotto + '%', cell_format)

            if Vuoto(quantita_grezza) and NonVuoto(prezzi_unitari_grezzi):
                lordo_totale = prezzi_unitari
                outSheet.write(j+10, 3, lordo_totale, cell_format)
                outSheet.write(j+10, 6, round(lordo_totale, 2), cell_format)
                somma_lordi_totali += lordo_totale
                #outSheet.write("D" + str(j+14), round(somma_lordi_totali, 2), bold_centrato)

            sconto_maggiorazione = pezzi[j].getElementsByTagName('ScontoMaggiorazione')
            if NonVuoto(sconto_maggiorazione):
                for k in range(len(sconto_maggiorazione)):
                    sconto_o_maggiorazione = (sconto_maggiorazione[k].getElementsByTagName('Tipo')[0].firstChild.data)#.encode("utf-8") VEDI RIGA 37
                    array_percentuale = sconto_maggiorazione[k].getElementsByTagName('Percentuale')
                    valore_sconto_grezzo = sconto_maggiorazione[k].getElementsByTagName('Importo')
                    if NonVuoto(array_percentuale):
                        if len(sconto_maggiorazione) == 1:
                            percentuale = float(array_percentuale[0].firstChild.data)
                            stringa_percentuale = str(percentuale)
                            if sconto_o_maggiorazione == "SC":
                                outSheet.write_string(j+10, 5, "-" + stringa_percentuale + "%", cell_format)
                                prezzi_unitari = ((100-percentuale)*prezzi_unitari)/100
                            if sconto_o_maggiorazione == "MG":
                                outSheet.write_string(j+10, 5, "+" + stringa_percentuale + "%", cell_format)
                                prezzi_unitari = ((100-percentuale)*prezzi_unitari)/100
                        if len(sconto_maggiorazione) > 1: #ci possono essere più sconti/maggiorazioni, quindi verifico se la lista che mi restituisce il .getElementsByTagName è lunga più di un elemento
                            percentuale = float(array_percentuale[0].firstChild.data)
                            stringa_percentuale = str(percentuale)
                            if sconto_o_maggiorazione == "SC":
                                stringa_tot = "-" + stringa_percentuale + "% " + stringa_tot
                                outSheet.write_string(j+10, 5, stringa_tot, cell_format)
                                prezzi_unitari = ((100-percentuale)*prezzi_unitari)/100
                            if sconto_o_maggiorazione == "MG":
                                stringa_tot = "+" + stringa_percentuale + "% " + stringa_tot
                                outSheet.write_string(j+10, 5, "+" + stringa_tot, cell_format)
                                prezzi_unitari = ((100-percentuale)*prezzi_unitari)/100
                    if NonVuoto(valore_sconto_grezzo):
                        valore_sconto = float(valore_sconto_grezzo[0].firstChild.data)
                        #sconto_totale += valore_sconto
                        prezzi_unitari += valore_sconto
                        outSheet.write(j+10, 4, valore_sconto, cell_format)
                stringa_tot = ""
                totale_scontato = prezzi_unitari*quantita
                outSheet.write(j+10, 6, round(totale_scontato, 2), cell_format_bold)
                sconto_numerico = totale_scontato - lordo_totale
                sconto_totale += sconto_numerico
                outSheet.write(j+10, 4, round(sconto_numerico, 2), cell_format_bold)

        if j<len(pezzi)-1: #PREZZO NETTO TOTALE SE CI SONO SCONTI CON LO STESSO NUMERO DI LINEA MA NON SCONTOCASSA
            prezzo1 = pezzi[j].getElementsByTagName('NumeroLinea')
            prezzo2 = pezzi[j+1].getElementsByTagName('NumeroLinea')
            if prezzo1[0].firstChild.data == prezzo2[0].firstChild.data:
                prezzo_lordo = float(pezzi[j].getElementsByTagName('PrezzoUnitario')[0].firstChild.data)
                sconto_linea = float(pezzi[j+1].getElementsByTagName('PrezzoUnitario')[0].firstChild.data)

                prezzo_netto = lordo_totale + sconto_linea
                outSheet.write(j+10, 6, round(prezzo_netto, 2), cell_format_bold)
                sconto_percentuale = round(((prezzo_netto*100)/lordo_totale)-100)
                sconto_percentuale_stringa = str(sconto_percentuale)
                outSheet.write_string(j+10, 5, sconto_percentuale_stringa + "%", cell_format_bold)

    y = str(j+13)
    z = str(j+14)
    outSheet.write_string("D" + y, "Totale Lordo", centrato)
    outSheet.write("D" + z, round(somma_lordi_totali, 2), bold_centrato)
    outSheet.write_string("D10", "Lordo Totale", centrato)
    outSheet.write_string("E10", "Sconto", centrato)
    outSheet.write_string("F10", "Sconto Perc", centrato)

    outSheet.write_string("G" + y, "Importo IVA", centrato)
    totale_imposta = float(xmldoc.getElementsByTagName('Imposta')[0].firstChild.data)
    outSheet.write("G" + z, totale_imposta, bold_centrato)

    outSheet.write_string("E" + y, "Sconto Tot", centrato)
    outSheet.write("E" + z, round(sconto_totale, 2), bold)
    outSheet.write_string("A" + y, "Totale Fattura", centrato)
    outSheet.write_string("F" + y, "Imponibile", centrato)
    dati_riepilogo = xmldoc.getElementsByTagName('DatiRiepilogo')
    totale_imponibile_grezzo= xmldoc.getElementsByTagName('ImponibileImporto')
    if len(totale_imponibile_grezzo) == 1:
        totale_imponibile = round(float(xmldoc.getElementsByTagName('ImponibileImporto')[0].firstChild.data), 3)
    else:
        totale_imponibile= float(0)
        for i in range(len(totale_imponibile_grezzo)):
            AliquotaIVA = dati_riepilogo[i].getElementsByTagName('AliquotaIVA')
            valore_AliquotaIVA = float(AliquotaIVA[0].firstChild.data)
            if len(totale_imponibile_grezzo) > 1 and valore_AliquotaIVA == 0:
                continue
            totale_imponibile += round(float(totale_imponibile_grezzo[i].firstChild.data), 3)

    importo_pagamento = xmldoc.getElementsByTagName('ImportoPagamento')
    if len(importo_pagamento) == 1:
        prezzo_da_pagare  = float(importo_pagamento[0].firstChild.data)
    else:
        prezzo_da_pagare= float(0)
        for i in range(len(importo_pagamento)):
            prezzo_da_pagare += round(float(importo_pagamento[i].firstChild.data), 3)
    #prezzo_da_pagare = xmldoc.getElementsByTagName('ImportoTotaleDocumento')[0].firstChild.data
    #prezzo_da_pagare = totale_imposta + totale_imponibile
    outSheet.write("A" + z, prezzo_da_pagare, grigio_centrato_bold)
    outSheet.write("F" + z, totale_imponibile, grigio_centrato_bold)
    outSheet.write_string("G10", "Netto", centrato)

    outSheet.set_paper(9) #9 è A4 https://xlsxwriter.readthedocs.io/page_setup.html
    outSheet.set_margins(left=0.45, right=0.35, top=0.75, bottom=0.75)
    outSheet.fit_to_pages(1, 0) # 1 page wide and as long as necessary.

    outExcel.close()

    o = win32com.client.Dispatch("Excel.Application")
    o.Visible = False

    wb_path = fatture_convertite_path + "/" + nome_excel + ".xlsx"

    wb = o.Workbooks.Open(wb_path)

    ws_index_list = [1] #indica quali sheets vuoi stampare, separandole con delle virgole

    path_to_pdf = program_path + "/Fatture PDF/" + nome_excel + ".pdf"

    wb.WorkSheets(ws_index_list).Select()

    wb.ActiveSheet.ExportAsFixedFormat(0, path_to_pdf)

    wb.Close(True)

    os.chdir(program_path)

    allegato_questionmark = xmldoc.getElementsByTagName('Allegati')
    if len(allegato_questionmark) > 0:
        allegato = allegato_questionmark[0].getElementsByTagName('Attachment')[0].firstChild.data
        # Decode the Base64 string, making sure that it contains only valid characters
        bytes = b64decode(allegato, validate=True)

        # Perform a basic validation to make sure that the result is a valid PDF file
        # Be aware! The magic number (file signature) is not 100% reliable solution to validate PDF files
        # Moreover, if you get Base64 from an untrusted source, you must sanitize the PDF contents
        if bytes[0:4] != b'%PDF':
            raise ValueError('Missing the PDF file signature')

    # Write the PDF contents to a local file
        os.chdir(program_path + "/Allegati")
        f = open(nome_excel + '.pdf', 'wb')
        f.write(bytes)
        f.close()# Decode the Base64 string, making sure that it contains only valid characters
     
        os.chdir(program_path)

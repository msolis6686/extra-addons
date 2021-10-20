# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer/supplier statement of account reports in Odoo ',
    'category': 'Accounting',
    'version': '13.0.0.3',
    'summary': 'Apps for print customer statement report print vendor statement payment reminder customer payment followup send customer statement print account statement reports print overdue statement reports send overdue statement print supplier statement reports',
    'description': """
                BrowseInfo developed a new odoo/OpenERP module apps
        This module use for Print Customer Statement Print Supplier Statement Send Customer Statement by email.
        Also shows the payment followup tab which show overdue balance and total amount overdue.
        Print Customer overdue payment Send overdue payment by email Calculate overdue balance based on Payment Terms also send payment reminder.
        Shows partner balance customer balance partner leadger account follow-up Payment Warning Payment Reminder.
        Print Customer Statement Print Supplier Statement Send Customer Statement by email Send supplier statement by email
        Account Statement Partner statement Balance Sheet ledger Report Print Account Statement Accounting Reports Statement Reports 
        Customer report Balance Statement Customer Balance Report Customer ledger report ledger balance.
        Credit Statement Debit Statement Customer Overdue statement Accounting Statement Creditor Reports Debtor Reports Account follow-up 
        Account followup report payment followup report payment follow-up Print Ledger report according to customer and supplier.
        Reporting function to generate statement of all transactions by partner vendor customer AR/AP for period/ All credits all debits.
        Account receivable report by period Account receivable report by customer With all transaction Credit Debit - REFER excel file Required Report AP-AR Statement for a period.
        Account Payable report by period Account Payable report by vendor WIth all transaction Credit Debit REFER excel file Required Report AP-AR Statement for a period.
        Customer statement by date So that we can see all open items in the system on that exact date REFER excel file 'Required Report' Statement of Account.
        Vendor statement by date So that we can see all open items in the system on that exact date REFER excel file 'Required Report'
        Customer statement by date So that we can see total amount for all open items in the system on that exact date only detailing GL accounts for these open items. REFER excel file required Report.
        invoice outstanding report invoice report invoice remaining amount report, invoice overdue report invoice outstanding excel report
        Vendor statement by date So that we can see total amount for all open items in the system on that exact date only detailing GL accounts for these open items. REFER excel file 'Required Report'
Openoo / OpenERP

openerp module for Print Customer Statement Print Supplier Statement.
        Send Customer Statement by email Send supplier statement by email 
        Account Statements Partner statement Balance Sheet ledger Report Print Account Statement Accounting Reports
        Statement Reports Customer report Balance Statement Customer Balance Report  Customer ledger report ledger balance.
        Odoo Customer Statement Odoo Supplier Statement Odoo Account Customer Supplier Statement
        Odoo Account Customer Statement Odoo Account Supplier Statement Customer overdue statement financial reporting 
        financial reports Accounting Statements financial Accounting Statements Supplier Statements reports 
        Customer financial Statement reports financial Statements reports in Odoo
        customer statement of account Supplier statement of account partner statement of account customer statement of account report 
        partner statement of account reports supplier statement of account reports
        Customer Accounting Statement reports Supplier Accounting Statement reports
        customer amount overdue customer payment overdue report customer total overdue customer balance partner balance reports 
        partner ledger supplier payment supplier remaining balance supplier balance statement of customer statement of partner
        statement of customer customer account statement supplier account statement customer bank statement customer followp send followup
        هذه الوحدة تستخدم لطباعة بيان العملاء ، طباعة بيان المورد. أرسل بيان العميل بالبريد الإلكتروني.
        يعرض أيضًا علامة التبويب "متابعة الدفع" التي تعرض الرصيد المتأخر والمبلغ الإجمالي المتأخر.
        طباعة دفع العملاء المتأخرة ، إرسال الدفع المتأخر عن طريق البريد الإلكتروني.حساب رصيد المتأخرة على أساس شروط الدفع أيضا إرسال تذكير الدفع.مشاهدة رصيد الشريك ، رصيد العملاء ، شريك القيادة ، حساب المتابعة. تحذير الدفع ، تذكير الدفع.
        طباعة بيان العملاء ، طباعة بيان المورد. إرسال بيان العملاء عن طريق البريد الإلكتروني. إرسال بيان المورد عن طريق البريد الإلكتروني. بيان الحساب ، بيان الشريك ، الميزانية العمومية ، تقرير دفتر الأستاذ ، بيان حساب الطباعة ، تقارير المحاسبة ، تقارير كشف الحساب ، تقرير العميل ، بيان الرصيد ، تقرير رصيد العميل ، تقرير دفتر الأستاذ الزبون ، رصيد دفتر الأستاذ. بيان الائتمان ، بيان الخصم .العميل المتأخرة البيان. بيان المحاسبة ، تقارير الدائن ، تقرير المدين. حساب الحالة - wup ، تقرير متابعة الحساب ، تقرير متابعة الدفع ، متابعة الدفع.
        تقرير دفتر الأستاذ طبقاً للعميل والمورد.
        وظيفة التقارير لتوليد بيان لجميع المعاملات من قبل الشريك (البائع / العميل) (AR / AP) ، للفترة / جميع الاعتمادات جميع الديون.
        تقرير الحسابات المستحقة القبض حسب الفترة ، تقرير المستحق القبض من قبل العميل. مع جميع المعاملات الائتمان ، الخصم - ملف اكسل REFER "تقرير مطلوب" بيان AP-AR لفترة.
        تقرير حساب مستحق الدفع حسب الفترة ، تقرير "حساب المدفوعات" من قبل البائع. من خلال جميع معاملات الائتمان ، وملف debit REFER excel 'Required Report' AP-AR Statement for a period.
        بيان العميل حسب التاريخ. حتى نتمكن من رؤية جميع العناصر المفتوحة في النظام في ذلك التاريخ المحدد ، يمكنك REFER excel file "Required Report" Account of Account.
        بيان البائع حسب التاريخ. حتى نتمكن من رؤية جميع العناصر المفتوحة في النظام في ذلك التاريخ المحدد REFER excel file "Required Report"
        بيان العميل حسب التاريخ. حتى يمكننا أن نرى المبلغ الإجمالي لجميع العناصر المفتوحة في النظام في ذلك التاريخ المحدد فقط بالتفصيل حسابات GL لهذه العناصر المفتوحة. REFER ملف اكسل المطلوبة التقرير.
        فاتورة تقرير معلق ، تقرير الفاتورة ، فاتورة المبلغ المتبقي ، فاتورة تقرير متأخرة ، فاتورة تقرير التفوق المعلقة
        بيان البائع حسب التاريخ. حتى يمكننا أن نرى المبلغ الإجمالي لجميع العناصر المفتوحة في النظام في ذلك التاريخ المحدد فقط بالتفصيل حسابات GL لهذه العناصر المفتوحة. REFER excel file "Required Report"
wadaeat BrowseInfo tatbiqat alwahdat aljadidat Openoo / OpenERP
        hidhih alwahdat tustakhdam litabaeat bayan aleumala' , tabaeat bayan almurid. 'ursil bayan aleamyl bialbarid al'iiliktruni.
        yierad aydana ealamat altabwib "mtabieat aldufea" alty taearad alrasid almuta'akhir walmablagh al'iijmaliu almuta'akhir.
        tabaeat dafe aleumala' almuta'akhirat , 'iirsal aldafe almuta'akhir ean tariq albarid al'iiliktruni.hisab rasid almuta'akhirat ealaa 'asas shurut aldafe 'aydaan 'iirsal tadhkir aldafe.mushahadat rasid alsharik , rasid aleumla' , sharik alqiadat , hisab almutabaeati. tahdhir aldafe , tadhkir aldafe.
        tibaeat bayan aleumala' , tibaeat bayan almurida. 'iirsal bayan aleumala' ean tariq albarid al'iiliktruni. 'iirsal bayan almurid ean tariq albarid al'iiliktruni. bayan alhisab , bayan alsharik , almizaniat aleumumiat , taqrir duftir al'ustadh , bayan hisab altibaeat , taqarir almuhasabat , taqarir kashf alhisab , taqrir aleamyl , bayan alrasid , taqrir rasid aleamyl , taqrir duftar al'ustadh alzubun , rasid daftar al'ustadh. bayan alaitiman , bayan alkhasm .aleamil almuta'akhirat albayan. bayan almuhasabat , taqarir aldaayin , taqrir almadin. hisab alhalat - wup , taqrir mutabaeat alhisab , taqrir mutabaeat aldafe , mutabaeat aldafe.
        tiqrir dufatar al'ustadh tbqaan lileamil walmurid.
        wazifat altaqarir litawlid bayan lajamie almueamalat min qibal alsharik (albayie / alemyl) (AR / AP) , lilfatrat / jmye alaietimadat jmye aldywn.
        tiqryr alhisabat almustahaqat alqabd hsb alfatrat , taqrir almustahaqi alqabd min qibal aleamil. mae jmye almueamalat alaitiman , alkhasm - milafa aksil REFER "tqarir matluba" bayan AP-AR lifatrat.
        taqrir hisab mustahiq aldafe hsb alfatrat , taqrir "hsaab almadfueat" min qibal albayie. min khilal jmye mueamalat alaituman , wamalf debit REFER excel 'Required Report' AP-AR Statement for a period.
        bian aleamyl hsb altaarikh. hataa nutumakan min ruyat jmye aleanasir almaftuhat fi alnizam fi dhalik alttarikh almuhadad , yumkinuk REFER excel file "Required Report" Account of Account.
        bian albayie hsb altaarikh. hataa natamakan min ruyat jmye aleanasir almaftuhat fi alnizam fi dhalik alttarikh almuhadad REFER excel file "Required Report"
        bian aleamyl hsb altaarikh. hataa ymknna 'an naraa almablagh al'iijmalia lajamie aleanasir almaftuhat fi alnizam fi dhalik alttarikh almuhadad faqat bialtafsil hisabat GL lihadhih aleanasir almaftuhati. REFER milafi aiksil almatlubat altaqrir.
        fatwrat taqrir muealaq , taqrir alfatwrt , faturat almablagh almutabaqii , faturat taqrir muta'akhirat , faturt taqrir altafawuq almuealaqa
        bian albayie hsb altaarikh. hataa ymknna 'an naraa almablagh al'iijmalia lajamie aleanasir almaftuhat fi alnizam fi dhalik alttarikh almuhadad faqat bialtafsil hisabat GL lihadhih aleanasir almaftuhati. REFER excel file "Required Report"
        BrowseInfo desarrolló un nuevo módulo odoo / OpenERP
        Este módulo se utiliza para Imprimir la declaración del cliente, Imprimir la declaración del proveedor. Enviar la declaración del cliente por correo electrónico.
        También muestra la pestaña de seguimiento de pagos que muestra el saldo vencido y la cantidad total vencida.
        Imprima el pago vencido del cliente, envíe el pago vencido por correo electrónico. Calcule el saldo vencido basado en las condiciones de pago y envíe un recordatorio de pago. Muestra el saldo del socio, el saldo del cliente, el interlocutor, el seguimiento de la cuenta. Aviso de pago, recordatorio de pago.
        Imprima la declaración del cliente, imprima la declaración del proveedor. Envíe la declaración del cliente por correo electrónico. Enviar declaración de proveedor por correo electrónico. Declaración de cuenta, declaración de socio, balance, informe de contabilidad, estado de cuenta de impresión, informes de contabilidad, informes de cuenta, informe del cliente, estado de cuenta, informe de saldo del cliente, informe de contabilidad del cliente, saldo del libro mayor. Declaración de crédito, declaración de débito . Declaración vencida del cliente. Estado de cuenta, informes de acreedor, informes de deudor. Cuenta a continuación, informe de seguimiento de cuenta, informe de seguimiento de pagos, seguimiento de pagos.
        Imprimir informe de libro según el cliente y el proveedor.
        Función de informe para generar la declaración de todas las transacciones por socio (proveedor / cliente) (AR / AP), para el período / Todos los créditos todos los débitos.
        Informe de cuentas por cobrar por período, informe de cuentas por cobrar por cliente. Con todas las transacciones de crédito, débito - REFER archivo Excel 'Informe requerido' AP-AR Declaración de un período.
        Informe de cuentas por pagar por período, informe de cuentas por pagar por proveedor. Con todo el crédito de la transacción, débito REMITIR el archivo Excel archivo 'Reporte requerido' Declaración AP-AR por un período.
        Declaración del cliente por fecha. Para que podamos ver todos los elementos abiertos en el sistema en esa fecha exacta REFERAR el archivo de Excel 'Reporte requerido'.
        Declaración del vendedor por fecha. Para que podamos ver todos los elementos abiertos en el sistema en esa fecha exacta REMITIR el archivo de Excel 'Reporte obligatorio'
        Declaración del cliente por fecha. Para que podamos ver el importe total de todos los elementos abiertos en el sistema en esa fecha exacta, solo se detallan las cuentas GL para estos elementos abiertos. REFER archivo de Excel requerido Informe.
        informe pendiente de factura, informe de factura, informe de cantidad restante de factura, informe vencido de factura, informe de Excel sobresaliente de factura
        Declaración del vendedor por fecha. Para que podamos ver el importe total de todos los elementos abiertos en el sistema en esa fecha exacta, solo se detallan las cuentas GL para estos elementos abiertos. REFERIR el archivo de Excel 'Reporte obligatorio'
BrowseInfo desenvolveu um novo app de módulo odoo / OpenERP
        Este módulo é usado para Imprimir a Declaração do Cliente, Imprimir a Declaração do Fornecedor. Enviar a Declaração do Cliente por email.
        Também mostra a guia de acompanhamento de pagamento que mostra o saldo vencido e o valor total vencido.
        Imprimir Pagamento atrasado do cliente, Enviar pagamento atrasado por e-mail.Calcule o saldo vencido com base nos Termos de pagamento e também envie um lembrete de pagamento.Somente saldo do parceiro, saldo do cliente, líder do parceiro, acompanhamento da conta.O aviso de pagamento, Lembrete de pagamento.
        Imprimir Declaração do Cliente, Imprimir Declaração do Fornecedor. Enviar a Declaração do Cliente por email. Enviar declaração de fornecedor por e-mail. Declaração de conta, declaração de parceiro, balanço, relatório de contabilidade, impressão conta declaração, relatórios contábeis, relatórios de declaração, relatório de cliente, declaração de saldo, relatório de saldo do cliente, relatório contábil, saldo contábil.Especificação de crédito, declaração de débito Declaração do cliente em atraso. Declaração contábil, relatórios do credor, relatórios do devedor. Conta follow-up, relatório de acompanhamento da conta, relatório de acompanhamento do pagamento, acompanhamento do pagamento.
        Imprimir relatório do razão de acordo com o cliente e o fornecedor.
        Função de geração de relatórios para gerar a demonstração de todas as transações por parceiro (fornecedor / cliente) (AR / AP), por período / Todos os créditos, todos os débitos.
        Relatório de contas a receber por período, Relatório de contas a receber pelo cliente. Com todas as transações Crédito, Débito - REFER excel file 'Relatório Obrigatório' Declaração AP-AR por um período.
        Relatório de contas a pagar por período, relatório de contas a pagar pelo fornecedor. Com toda a transação Crédito, débito REFER excel arquivo 'relatório exigido' declaração AP-AR por um período.
        Declaração do cliente por data. Para que possamos ver todos os itens em aberto no sistema na mesma data REFER excel arquivo 'Requerido Relatório' Declaração de Conta.
        Declaração do fornecedor por data. Para que possamos ver todos os itens em aberto no sistema na mesma data REFER excel file 'Required Report'
        Declaração do cliente por data. Assim, podemos ver o montante total de todas as partidas em aberto no sistema nessa data exata, apenas detalhando as contas contábeis para esses itens em aberto. REFER excel file required Relatório.
        relatório de fatura pendente, relatório de fatura, relatório de valor restante da fatura, relatório de faturamento vencido, relatório de exceções de faturamento excelente
        Declaração do fornecedor por data. Assim, podemos ver o montante total de todas as partidas em aberto no sistema nessa data exata, apenas detalhando as contas contábeis para esses itens em aberto. REFERIR arquivo excel 'Relatório Requerido'
BrowseInfo a développé un nouveau module odoo / OpenERP
        Ce module est utilisé pour Imprimer la déclaration du client, Imprimer la déclaration du fournisseur. Envoyer la déclaration du client par courrier électronique.
        Affiche également l'onglet Suivi des paiements qui indique le solde en souffrance et le montant total en retard.
        Imprimer le paiement en retard du client, envoyer le paiement en retard par e-mail.Calculer solde en souffrance basé sur les termes de paiement envoyer également rappel de paiement.Affiche solde du partenaire, solde client, partenaire partenaire, suivi du compte.Avertissement de paiement, rappel de paiement.
        Imprimer la déclaration du client, imprimer la déclaration du fournisseur .Envoyer la déclaration du client par courriel. Envoyer la déclaration du fournisseur par e-mail. Relevé de compte, relevé de partenaire, bilan, relevé de compte, relevé de compte, rapports de comptabilité, relevés de compte, rapport client, relevé de solde, relevé de solde client, relevé de grand livre. .Compte client en retard. Relevé de compte, rapports de créancier, rapports de débiteur. Compte suivi, rapport de suivi de compte, rapport de suivi de paiement, suivi de paiement.
        Impression du rapport Ledger en fonction du client et du fournisseur.
        Fonction de reporting pour générer une déclaration de toutes les transactions par partenaire (fournisseur / client) (AR / AP), pour période / Tous les crédits tous les débits.
        Rapport de compte à recevoir par période, Rapport de compte à recevoir par client. Avec toutes les transactions Credit, Debit - REFER excel file 'Rapport requis' AP-AR Statement pour une période.
        Rapport sur les comptes payables par période, rapport sur les comptes fournisseurs par fournisseur. Avec toutes les transactions Crédit, Débit REFER excel fichier 'Rapport requis' Déclaration AP-AR pour une période.
        Déclaration du client par date. Afin que nous puissions voir tous les éléments ouverts dans le système à cette date exacte, veuillez REFERER le fichier Excel 'Compte rendu requis' Relevé de compte.
        Déclaration du fournisseur par date. Afin que nous puissions voir tous les éléments ouverts dans le système à cette date exacte REFER excel file 'Rapport requis'
        Déclaration du client par date. Afin que nous puissions voir le montant total de tous les postes non soldés dans le système à cette date précise, en ne détaillant que les comptes GL pour ces postes non soldés. REFERER le fichier Excel requis Rapport.
        rapport en suspens de la facture, rapport de la facture, rapport de la quantité restante de la facture, rapport en retard de la facture, rapport excel de la facture exceptionnelle
        Déclaration du fournisseur par date. Afin que nous puissions voir le montant total de tous les postes non soldés dans le système à cette date précise, en ne détaillant que les comptes GL pour ces postes non soldés. Fichier REFER excel 'Rapport requis'
BrowseInfo heeft een nieuwe odoo / OpenERP-module-apps ontwikkeld
        Deze module wordt gebruikt voor Print Customer Statement, Print Supplier Statement. Stuur de klantverklaring per e-mail.
        Toont ook het tabblad met de betalingsupdates dat het achterstallige saldo en het totale achterstallige bedrag laat zien.
        Afdrukken Achterstallige betaling van klant, achterstallige betaling per e-mail verzenden. Bereken achterstallige saldo op basis van betalingsvoorwaarden ook betalingsherinnering. Toont partnerbalans, klantensaldo, partner leadger, account-follow-up. Betalingswaarschuwing, betalingsherinnering.
        Klantverklaring afdrukken, Leverancierverklaring afdrukken. Stuur de klantverklaring per e-mail. Verzend de leveranciersverklaring per e-mail. Accounting, partnerafschrift, balans, grootboekrapport, afdrukrekeningoverzicht, boekhoudrapporten, overzichtsrapporten, klantrapport, balansoverzicht, klantensaldo-rapport, klantgrootboek, grootboeksaldo. Credit Statement, debetoverzicht . Betalingsachterstandsverklaring. Accountingverklaring, crediteurenrapporten, debiteurenrapporten. Accountopvolging, accountopvolgingsrapport, follow-uprapport voor betalingen, betalingsopvolging.
        Grootboekrapport afdrukken volgens klant en leverancier.
        Rapporteringsfunctie voor het genereren van overzicht van alle transacties door partner (leverancier / klant) (AR / AP), voor periode / Alle credits voor alle afschrijvingen.
        Debiteurenverslag per periode, Debiteurenverslag per klant. Met alle transactie Krediet, Debet - REFER excelbestand 'Vereist Rapport' AP-AR Verklaring voor een periode.
        Rapport 'Te betalen per rekening per periode', rapport 'Te betalen rekeningen' per leverancier. Met alle transactiekredieten, debet REFER excelbestand 'Vereist rapport' AP-AR verklaring voor een periode.
        Klantverklaring op datum. Zodat we op die exacte datum alle openstaande items in het systeem kunnen zien. REFER excelbestand 'Vereist rapport' Statement of Account.
        Leveranciersoverzicht op datum. Zodat we alle openstaande items in het systeem op die exacte datum kunnen zien. REFER excelbestand 'Vereist rapport'
        Klantverklaring op datum. Zodat we het totale bedrag voor alle open posten in het systeem op die exacte datum kunnen zien met alleen gedetailleerde GL-rekeningen voor deze open posten. REFER excel-bestand vereist rapport.
        openstaand factuurrapport, factuurrapport, resterend factuurrapport, achterstallige factuurrapport, openstaande excel-rapport
        Leveranciersoverzicht op datum. Zodat we het totale bedrag voor alle open posten in het systeem op die exacte datum kunnen zien met alleen gedetailleerde GL-rekeningen voor deze open posten. REFER excel-bestand 'Vereist rapport'
BrowseInfo entwickelte ein neues odoo / OpenERP Modul Apps
        Dieses Modul verwenden Sie für Print Customer Statement, Drucken Supplier Statement.Send Customer Statement per E-Mail.
        Zeigt auch die Registerkarte Zahlungsnachverfolgung an, die überfälliges Guthaben und überfälligen Gesamtbetrag anzeigen.
        Drucken Überfällige Kundenzahlung, Überfällige Zahlung per E-Mail senden. Überfälliges Guthaben basierend auf den Zahlungsbedingungen berechnen, außerdem eine Zahlungserinnerung senden. Zeigt das Partner-Guthaben, den Kundensaldo, den Partner-Leadger, die Kontobewegung, die Zahlungswarnung und die Zahlungserinnerung an.
        Kundenerklärung drucken, Lieferantenerklärung drucken. Kundenerklärung per E-Mail senden. Versenden Sie die Lieferantenerklärung per E-Mail. Kontoauszug, Partnererklärung, Bilanz, Hauptbuchbericht, Kontoauszug drucken, Buchhaltungsberichte, Kontoauszüge, Kundenbericht, Kontoauszug, Kundensaldobericht, Debitorenbuchhaltung, Kontostand. Kreditnachweis, Sollauszug .Customer Überfällige Anweisung.Accounting-Anweisung, Creditor Reports, Debtor Reports.Account Follow-up, Konto Follow-up-Bericht, Zahlung Follow-up-Bericht, Zahlung Follow-up.
        Print Ledger Bericht nach Kunden und Lieferanten.
        Reporting-Funktion zur Erstellung einer Abrechnung aller Transaktionen nach Partner (Kreditor / Kunde) (AR / AP), für Zeitraum / Alle Kredits alle Belastungen.
        Kontobewegung nach Periode, Debitorenbericht nach Kunde. Mit allen Transaktion Credit, Debit - REFER Excel-Datei 'Required Report' AP-AR-Anweisung für einen Zeitraum.
        Kontobuch Bericht nach Zeitraum, Kreditorenbericht nach Kreditor. Mit allen Transaktion Credit, Debit REFER Excel-Datei 'Erforderlicher Bericht' AP-AR-Anweisung für einen Zeitraum.
        Kundenerklärung nach Datum. Damit wir alle offenen Posten im System an diesem genauen Datum sehen können, REFER Excel-Datei 'Erforderliche Bericht' Kontoauszug.
        Lieferantenerklärung nach Datum Damit wir alle offenen Elemente im System an genau diesem Datum sehen können, REFER Excel-Datei 'Erforderlicher Bericht'
        Kundenerklärung nach Datum. Damit wir den Gesamtbetrag für alle offenen Posten im System an diesem genauen Datum sehen können, werden nur die Hauptbuchkonten für diese offenen Posten angezeigt. REFER Excel-Datei erforderlich Bericht.
        Rechnung ausstehenden Bericht, Rechnung Bericht, Rechnung Restbetrag Bericht, Rechnung überfälligen Bericht, Rechnung ausstehenden Excel-Bericht
        Lieferantenerklärung nach Datum Damit wir den Gesamtbetrag für alle offenen Posten im System an diesem genauen Datum sehen können, werden nur die Hauptbuchkonten für diese offenen Posten angezeigt. REFER Excel-Datei 'Erforderlicher Bericht'

Module use for invoice followup Account followup Payment Followup Customer followup for invoice 
    Send letter for invoice Send followup email Send email for outstading payment send email for overdue payment.
    Account follow-up management Customer follow-up management Account payment follow-up Account customer follow-up 
    follow-up payment management followup account management Outstading customer followup outstanding followup outstanding payment followup
Payment Followup payment reminder bill reminder unpaid bill followup email payment followup late invoices reminder
invoices reminder invoice reminder invoices followup Late Payment followup overdue followup Late Payment reminder
Late Payment Was Due Email Reminders for Overdue Payments late payments Email Reminders late payments for Overdue Payments Email late payments

Module gebruik voor factuur follow-up, account follow-up, betaling follow-up, klant follow-up voor factuur, stuur brief voor factuur, stuur follow-up e-mail. Stuur e-mail voor betaling buiten de stad, stuur e-mail voor achterstallige betaling. Beheer opvolging van de klant, Follow-up klantbeheer, Follow-up accountbetaling, Follow-up account klant, follow-uppaymentbeheer, follow-up accountbeheer, follow-up klanten Outstading, uitstekende follow-up, openstaande betalingsupdate
Modulbenutzung für Rechnungsverfolgung, Kontoverfolgung, Zahlungsnachverfolgung, Kundennachverfolgung für Rechnung, Senden eines Briefes für Rechnung, Senden einer Folge-E-Mail. Senden Sie E-Mails zur Zahlungserfassung, senden Sie E-Mails für überfällige Zahlungen.Account-Folgemanagement, Kundenfolgemanagement, Nachverfolgung von Kontozahlungen, Konto-Kunden-Follow-up, Follow-up-Zahlungsverwaltung, Follow-up-Kontoverwaltung, Outstading-Kunden-Followup, hervorragendes Follow-up, ausstehende Zahlungsnachfolge
Utilisation du module pour le suivi des factures, le suivi du compte, le suivi des paiements, le suivi client pour la facture, l'envoi d'une lettre pour la facture, l'envoi d'un courrier électronique de suivi. Envoyer un e-mail pour un paiement échu, envoyer un e-mail pour un retard de paiement.Gestion de suivi de compte, suivi de client, suivi de compte, suivi de compte client, gestion des paiements de suivi, gestion de compte de suivi, suivi client Outstading, suivi exceptionnel, suivi de paiement exceptionnel
Uso del módulo para seguimiento de facturas, Seguimiento de cuentas, Seguimiento de pagos, Seguimiento de clientes para facturas, Enviar carta para factura, Enviar seguimiento de correo electrónico. Envíe un correo electrónico para pagos pendientes, envíe un correo electrónico por pagos atrasados. Gestión de seguimiento de cuentas, gestión de seguimiento de clientes, seguimiento de pagos de cuentas, seguimiento de clientes de cuentas, seguimiento de gestión de pagos, seguimiento de gestión de cuentas, seguimiento de clientes sobresaliente, seguimiento excepcional, seguimiento de pago pendienteso do módulo para acompanhamento de faturas, Acompanhamento de conta, Acompanhamento de pagamento, Acompanhamento de cliente para fatura, Enviar carta para fatura, Enviar email de acompanhamento. Enviar e-mail para outstading pagamento, enviar e-mail para pagamento em atraso.Gerenciamento de acompanhamento de conta, gerenciamento de acompanhamento do cliente, acompanhamento de pagamento de conta, acompanhamento de cliente de conta, gerenciamento de pagamento de acompanhamento, gerenciamento de contas de acompanhamento, acompanhamento de cliente Outstading, acompanhamento pendente, acompanhamento de pagamento pendente
Module gebruik voor factuur follow-up, account follow-up, betaling follow-up, klant follow-up voor factuur, stuur brief voor factuur, stuur follow-up e-mail. Stuur e-mail voor betaling buiten de stad, stuur e-mail voor achterstallige betaling. Beheer opvolging van de klant, Follow-up klantbeheer, Follow-up accountbetaling, Follow-up account klant, follow-uppaymentbeheer, follow-up accountbeheer, follow-up klanten Outstading, uitstekende follow-up, openstaande betalingsupdateاستخدام وحدة لمتابعة الفاتورة ، متابعة الحساب ، متابعة الدفع ، متابعة العملاء للفاتورة ، إرسال رسالة للفاتورة ، إرسال البريد الإلكتروني للمتابعة. إرسال البريد الإلكتروني لدفع outstading ، إرسال البريد الإلكتروني للدفع المتأخرة. إدارة متابعة الحساب ، إدارة متابعة العملاء ، متابعة الدفع الحساب ، متابعة العملاء الحساب ، إدارة الدفع المتابعة ، إدارة حساب المتابعة ، متابعة العملاء Outstading ، المتابعة المتميزة ، ومتابعة الدفع المعلقة
aistikhdam wahdat limutabaeat alfatwrt , mutabaeat alhisab , mutabaeat aldafe , mutabaeat aleumala' lilfaturat , 'iirsal risalat lilfaturat , 'iirsal albarid al'iiliktrunii lilmutabaeata. 'iirsal albarid al'iiliktrunii lidafe outstading ، 'iirsal albarid al'iiliktrunii lildafe almuta'akhirati. 'iidarat mutabaeat alhisab , 'iidarat mutabaeat aleumla' , mutabaeat aldafe alhisab , mutabaeat aleumala' alhisab , 'iidarat aldafe almutabaeat , 'iidarat hisab almutabaeat , mutabaeat aleumla' Outstading , almutabaeat almutamayizat , wamutabaeat aldafe almuealaq
""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'images': [],
    'depends': ['base', 'account', 'sale_management', 'mail', 'sales_team'],
    
    'data': ['security/ir.model.access.csv',
            'views/report.xml',
             'views/customer_statement_report.xml',
             'views/supplier_statement_report.xml',
             'views/monthly_customer_statement_report.xml',
             'views/mail_data.xml',
             'views/res_partner_view.xml',
             'views/overdue_report.xml',
             'data/account_email_template_data.xml',
    ],
    'installable': True,
    'price': 36,
    'currency': "EUR",
    'auto_install': False,
    'application': True,
    "images":["static/description/Banner.png"],
    'live_test_url':'https://youtu.be/Sg2OC9RLiTY',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

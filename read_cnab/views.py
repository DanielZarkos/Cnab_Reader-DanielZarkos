from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadFile, Transaction

# Dict for Transactions:
TYPE_MAPPING = {
    "1": "Débito",
    "2": "Boleto",
    "3": "Financiamento",
    "4": "Crédito",
    "5": "Empréstimo",
    "6": "Vendas",
    "7": "TED",
    "8": "DOC",
    "9": "Aluguel",
}


def upload_file(request):
    if request.method == "POST":
        file = request.FILES["file"]

        cnab_file = UploadFile.objects.create(cnab_file=file)
        cnab_file.save()

        saldo_total = 0
        operacoes = []

        with open(
            f"uploads/{str(cnab_file.cnab_file)}", "r", encoding="utf-8"
        ) as read_file:
            for file_line in read_file:
                tipo = TYPE_MAPPING[file_line[:1]]
                data = f"{file_line[7:9]}/{file_line[5:7]}/{file_line[1:5]}"
                valor = int(file_line[9:19]) / 100
                cpf = file_line[19:30]
                cartao = file_line[30:42]
                horario = f"{file_line[42:44]}:{file_line[44:46]}:{file_line[46:48]}"
                dono = file_line[48:62]
                loja = file_line[62:81]

                transaction = Transaction.objects.create(
                    tipo=tipo,
                    data=data,
                    valor=valor,
                    cpf=cpf,
                    cartao=cartao,
                    hora=horario,
                    dono=dono,
                    loja=loja,
                )
                transaction.save()
                operacoes.append(transaction)

                if tipo in ["Boleto", "Financiamento", "Aluguel"]:
                    saldo_total -= valor
                    print(-valor)

                else:
                    saldo_total += valor
                    print(valor)

        return render(
            request,
            "resultados.html",
            context={"transactions": operacoes, "saldo_total": saldo_total},
        )

    else:
        form = UploadFileForm()
        return render(request, "upload.html", {"form": form})

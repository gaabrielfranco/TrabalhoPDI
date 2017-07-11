#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 13:54:42 2017

@author: marcos
"""

#==============================================================================
# Importa modulos relacionados a GUI
#==============================================================================
import tkinter.constants as cte
from tkinter import Tk
from tkinter import Frame, Menu
from tkinter import LabelFrame, Label, Button, Scrollbar, Toplevel, Scale
from tkinter import Canvas, Radiobutton
from tkinter import filedialog as tkf
from PIL import ImageTk
from tkinter import messagebox as tkm
from tkinter import StringVar

#==============================================================================
# Outros modulos
#==============================================================================
import os
from classes.imagem import Imagem
import modulos.cores as cor

class Gui(Frame):
#==============================================================================
#     Metodos Basicos
#==============================================================================
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        # Atributos GUI
        self.parent = parent
        self.file_opt = self.flopt = {}
        w,h = self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()
        self.largura = w - 20
        self.altura = h - 20

        # Atributos funcionais
        self.img = None
        self.imgOld = None
        self.arqImg = StringVar()
        self.arqImg.set('')

        self.formatos = {}
        self.formatos['gif'] = 'GIF'
        self.formatos['jpg'] = 'JPEG'
        self.formatos['jpeg'] = 'JPEG'
        self.formatos['png'] = 'PNG'
        self.formatos['bmp'] = 'BMP'
        self.formatos['tif'] = 'TIFF'
        self.formatos['tiff'] = 'TIFF'
        self.formatos['ppm'] = 'PPM'
        self.formatos['pbm'] = 'PPM'
        self.formatos['pgm'] = 'PPM'

        self.tipos = [('Imagens', ('*.jpg', '*.png', '*.gif', '*.bmp', '*.ppm', '*.pgm', '*.pbm')),('JPEG', '*.jpg'), ('PNG', '*.png'), ('GIF', '*.gif'), ('BMP', '*.bmp'), ('PPM', '*.ppm'), ('PGM', '*.pgm'), ('PBM', '*.pbm'), ('Todos arquivos', '*')]

        # Cria/atualiza GUI
        self.createWidgets()
        self.update_idletasks()

#==============================================================================
#     Metodos relacionados ao comportamento da GUI
#==============================================================================

    def createWidgets(self):
        self.canvas = Canvas(self.parent, width=1366, height=768)
        self.scroll = Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Configura barra de menus
        self.menubar = Menu(self.parent)
        self.parent.config(menu=self.menubar)

        # Menu arquivo e suas opcoes
        self.menuArquivo = Menu(self.menubar)
        self.menuArquivo.add_command(label='Abrir', underline=0, command=self.abrir)
        self.menuArquivo.add_separator()
        self.menuArquivo.add_command(label='Salvar', underline=0, command=self.salvar)
        self.menuArquivo.add_command(label='Salvar Como...', underline=0, command=self.salvarComo)
        self.menuArquivo.add_separator()
        self.menuArquivo.add_command(label='Fechar imagem(ns)', underline=0, command=self.fecharArquivo)
        self.menuArquivo.add_command(label="Sair", underline=3, command=self.onExit)
        self.menubar.add_cascade(label="Arquivo", underline=0, menu=self.menuArquivo)

        # Menu editar e suas opcoes
        self.menuEditar = Menu(self.menubar)
        self.menuEditar.add_command(label='Desfazer', underline=0, command=self.desfazer)
        self.menubar.add_cascade(label="Editar", underline=0, menu=self.menuEditar)

        # Menu Imagem e suas opcoes
        self.menuImagem = Menu(self.menubar)

        self.submenuDominioFreq = Menu(self.menuImagem)
        self.submenuDominioFreq.add_command(label='Filtro passa-baixa', underline=0, command=lambda:self.frequencia('passa-baixa'))
        self.submenuDominioFreq.add_command(label='Filtro passa-alta', underline=0, command=lambda:self.frequencia('passa-alta'))
        self.submenuDominioFreq.add_command(label='Filtro passa-faixa', underline=0, command=lambda:self.frequencia('passa-faixa'))
        self.submenuDominioFreq.add_command(label='Butterworth passa-baixa', underline=0, command=lambda:self.frequencia('butterworthPB'))
        self.submenuDominioFreq.add_command(label='Butterworth passa-alta', underline=0, command=lambda:self.frequencia('butterworthPA'))

        self.submenuEspaciais = Menu(self.menuImagem)
        self.submenuEspaciais.add_command(label='Erosão', underline=0, command=lambda:self.espaciais('erosao'))
        self.submenuEspaciais.add_command(label='Dilatação', underline=0, command=lambda:self.espaciais('dilatacao'))
        self.submenuEspaciais.add_command(label='Vidro v1', underline=0, command=lambda:self.espaciais('vidro1'))
        self.submenuEspaciais.add_command(label='Vidro v2', underline=0, command=lambda:self.espaciais('vidro2'))
        self.submenuEspaciais.add_command(label='Pixelização', underline=0, command=lambda:self.espaciais('pixelizacao'))
        
        self.submenuSuavicacao = Menu(self.menuImagem)
        self.submenuSuavicacao.add_command(label='Média', underline=0, command=lambda:self.suavicacao('media'))
        self.submenuSuavicacao.add_command(label='Gaausiana', underline=0, command=lambda:self.suavicacao('gaausiana'))
        self.submenuSuavicacao.add_command(label='Mediana', underline=0, command=lambda:self.suavicacao('mediana'))
        self.submenuSuavicacao.add_command(label='Conservativa', underline=0, command=lambda:self.suavicacao('conservativa'))

        self.submenuCombinacoes = Menu(self.menuImagem)
        self.submenuCombinacoes.add_command(label='Menor cor', underline=0, command=lambda:self.operacoesPP('combmenor'))
        self.submenuCombinacoes.add_command(label='Maior cor', underline=0, command=lambda:self.operacoesPP('combmaior'))
        self.submenuCombinacoes.add_command(label='Linear', underline=0, command=lambda:self.operacoesPP('comblinear'))
        self.submenuCombinacoes.add_command(label='Sigmóide horizontal', underline=0, command=lambda:self.operacoesPP('combsigmoideX'))
        self.submenuCombinacoes.add_command(label='Sigmóide vertical', underline=0, command=lambda:self.operacoesPP('combsigmoideY'))

        self.submenuOperacoesPP = Menu(self.menuImagem)
        self.submenuOperacoesPP.add_command(label='Soma', underline=0, command=lambda:self.operacoesPP('soma'))
        self.submenuOperacoesPP.add_command(label='Subtração', underline=0, command=lambda:self.operacoesPP('sub'))
        self.submenuOperacoesPP.add_command(label='Multiplicação', underline=0, command=lambda:self.operacoesPP('mult'))
        self.submenuOperacoesPP.add_command(label='Divisão', underline=0, command=lambda:self.operacoesPP('div'))
        self.submenuOperacoesPP.add_cascade(label='Combinação', underline=0, menu=self.submenuCombinacoes)
        

        self.submenuLinhas = Menu(self.menuImagem)
        self.submenuLinhas.add_command(label='Horizontais', underline=0, command=lambda:self.filtragemEspacial('linhas1'))
        self.submenuLinhas.add_command(label='Verticais', underline=0, command=lambda:self.filtragemEspacial('linhas2'))
        self.submenuLinhas.add_command(label='Ângulo em 45°', underline=0, command=lambda:self.filtragemEspacial('linhas3'))
        self.submenuLinhas.add_command(label='Ângulo em -45°', underline=0, command=lambda:self.filtragemEspacial('linhas4'))
        self.submenuLinhas.add_command(label='4 direções combinadas', underline=0, command=lambda:self.filtragemEspacial('linhas5'))

        self.submenuAgucamento = Menu(self.menuImagem)
        self.submenuAgucamento.add_command(label='Vizinhança 4', underline=0, command=lambda:self.filtragemEspacial('agucamento4'))
        self.submenuAgucamento.add_command(label='Vizinhança 8', underline=0, command=lambda:self.filtragemEspacial('agucamento8'))

        self.submenuLaplace = Menu(self.menuImagem)
        self.submenuLaplace.add_command(label='Sem bordas exteriores', underline=0, command=lambda:self.filtragemEspacial('laplace1'))
        self.submenuLaplace.add_command(label='Sem bordas interiores', underline=0, command=lambda:self.filtragemEspacial('laplace2'))
        self.submenuLaplace.add_command(label='Realçe com reconstrução do fundo', underline=0, command=lambda:self.filtragemEspacial('laplace3'))

        self.submenuFiltragemEspacial = Menu(self.menuImagem)
        self.submenuFiltragemEspacial.add_command(label='Roberts', underline=0, command=lambda:self.filtragemEspacial('roberts'))
        self.submenuFiltragemEspacial.add_command(label='Prewitt', underline=0, command=lambda:self.filtragemEspacial('prewitt'))
        self.submenuFiltragemEspacial.add_command(label='Sobel', underline=0, command=lambda:self.filtragemEspacial('sobel'))
        self.submenuFiltragemEspacial.add_cascade(label='Laplaciano', underline=0, menu=self.submenuLaplace)
        self.submenuFiltragemEspacial.add_command(label='Scharr', underline=0, command=lambda:self.filtragemEspacial('scharr'))
        self.submenuFiltragemEspacial.add_cascade(label='Linhas', underline=0, menu=self.submenuLinhas)
        self.submenuFiltragemEspacial.add_command(label='Emboss', underline=0, command=lambda:self.filtragemEspacial('emboss'))
        self.submenuFiltragemEspacial.add_cascade(label='Aguçamento', underline=0, menu=self.submenuAgucamento)
        self.submenuFiltragemEspacial.add_command(label='Relevo', underline=0, command=lambda:self.filtragemEspacial('relevo'))

        self.submenuConverte = Menu(self.menuImagem)
        self.submenuConverte.add_command(label='Colorido RGB', underline=0, command=lambda:self.converte('RGB'))
        self.submenuConverte.add_command(label='Colorido RGBA', underline=0, command=lambda:self.converte('RGBA'))
        self.submenuConverte.add_command(label='Escala de cinza', underline=0, command=lambda:self.converte('L'))
        self.submenuConverte.add_command(label='Binario', underline=0, command=lambda:self.converte('1'))

        self.submenuComparaImg = Menu(self.menuImagem)
        self.submenuComparaImg.add_command(label='Raiz do Erro Médio Quadrático', underline=0, command=lambda:self.comparaImagens('rmse'))
        self.submenuComparaImg.add_command(label='Coeficiente de Jaccard', underline=0, command=lambda:self.comparaImagens('jaccard'))

        self.menuImagem.add_command(label='Informacoes gerais', underline=0, command=self.info)
        self.menuImagem.add_separator()
        self.menuImagem.add_cascade(label='Converter', underline=0, menu=self.submenuConverte)
        self.menuImagem.add_separator()
        self.menuImagem.add_cascade(label='Comparação de imagens', underline=0, menu=self.submenuComparaImg)
        self.menuImagem.add_cascade(label='Detecção de descontinuidade', underline=0, menu=self.submenuFiltragemEspacial)
        self.menuImagem.add_cascade(label='Operações ponto a ponto', underline=0, menu=self.submenuOperacoesPP)
        self.menuImagem.add_cascade(label='Suavização', underline=0, menu=self.submenuSuavicacao)
        self.menuImagem.add_cascade(label='Filtros espaciais', underline=0, menu=self.submenuEspaciais)
        self.menuImagem.add_cascade(label='Filtros no domínio da frequência', underline=0, menu=self.submenuDominioFreq)
        self.menubar.add_cascade(label="Imagem", underline=0, menu=self.menuImagem)

        # Menu de operacoes sobre cores e suas opcoes
        self.menuCores = Menu(self.menubar)

        self.submenuCinza = Menu(self.menuCores)
        self.submenuCinza.add_command(label='Decomposicao de Maximo', underline=18, command=lambda:self.mudaCor('max'))
        self.submenuCinza.add_command(label='Decomposicao de Minimo', underline=18, command=lambda:self.mudaCor('min'))
        self.submenuCinza.add_command(label='Average', underline=0, command=lambda:self.mudaCor('average'))
        self.submenuCinza.add_command(label='Lightness', underline=0, command=lambda:self.mudaCor('lightness'))
        self.submenuCinza.add_command(label='Luminosity', underline=0, command=lambda:self.mudaCor('luminosity'))
        self.submenuCinza.add_command(label='Componente R', underline=11, command=lambda:self.mudaCor('r'))
        self.submenuCinza.add_command(label='Componente G', underline=11, command=lambda:self.mudaCor('g'))
        self.submenuCinza.add_command(label='Componente B', underline=11, command=lambda:self.mudaCor('b'))
        self.submenuCinza.add_command(label='Quantidade arbitraria de tons', underline=0, command=self.qnteArbitraria)

        self.submenuHalftone = Menu(self.menuCores)
        self.submenuHalftone.add_command(label='Bayer 2x2', underline=6, command=lambda:self.halftoning('bayer2'))
        self.submenuHalftone.add_command(label='Bayer 5x5', underline=6, command=lambda:self.halftoning('bayer5'))
        self.submenuHalftone.add_command(label='Atkinson', underline=0, command=lambda:self.halftoning('atkinson'))
        self.submenuHalftone.add_command(label='Sierra Lite', underline=0, command=self.emConstrucao)
        self.submenuHalftone.add_command(label='Jarvis, Judice, and Ninke', underline=0, command=self.emConstrucao)
        self.submenuHalftone.add_command(label='Floyd-Steinberg', underline=0, command=lambda:self.halftoning('floyd'))

        self.submenuPseudobinaria = Menu(self.menuCores)
        self.submenuPseudobinaria.add_command(label='Clustering', underline=0, command=lambda:self.binaria('padrao'))
        self.submenuPseudobinaria.add_command(label='Limiar', underline=0, command=lambda:self.binaria('limiar'))

        self.submenuHistograma = Menu(self.menuCores)
        self.submenuHistograma.add_command(label='Equalização de Histograma', underline=0, command=self.equalizacaoHistograma)
        self.submenuHistograma.add_command(label='Visualização de Histograma', underline=0, command=self.visualizacaoHistogramas)
        self.submenuHistograma.add_command(label='Especialização Direta de Histograma', underline=0, command=self.especificacaoDiretaHistograma)

        self.submenuRuidos = Menu(self.menuCores)
        self.submenuRuidos.add_command(label='Sal pimenta', underline=0, command=self.salPimenta)
        self.submenuRuidos.add_command(label='Ruído gaausiano', underline=0, command=self.ruidoGaausiano)

        self.menuCores.add_cascade(label='Tons de cinza', underline=0, menu=self.submenuCinza)
        self.menuCores.add_command(label='Inverter', underline=0, command=lambda:self.mudaCor('inv'))
        self.menuCores.add_command(label='Sepia', underline=0, command=lambda:self.mudaCor('sepia'))
        self.menuCores.add_separator()
        self.menuCores.add_cascade(label='Pseudo Binária', underline=0, menu=self.submenuPseudobinaria)
        self.menuCores.add_separator()
        self.menuCores.add_cascade(label='Halftoning', underline=0, menu=self.submenuHalftone)
        self.menuCores.add_separator()
        self.menuCores.add_command(label='Cisalhamento de Cor', underline=0, command=self.emConstrucao)
        self.menuCores.add_command(label='Balanco de cores', underline=0, command=self.balancoCor)
        self.menuCores.add_command(label='Quantização de cores', underline=0, command=self.quantizacaoCores)
        self.menuCores.add_separator()
        self.menuCores.add_command(label='Ajuste de brilho e contraste', underline=0, command=lambda:self.brilhoContraste())
        self.menuCores.add_command(label='Alargamento de contraste', underline=0, command=self.alargamentoContraste)
        self.menuCores.add_separator()
        self.menuCores.add_cascade(label='Histogramas', underline=0, menu=self.submenuHistograma)
        self.menuCores.add_cascade(label='Ruídos', underline=0, menu=self.submenuRuidos)
        self.menubar.add_cascade(label="Cores", underline=0, menu=self.menuCores)

        # Menu de operacoes topologicas e suas opcoes
        self.menuTopologia = Menu(self.menubar)
        self.menuTopologia.add_command(label='Rotular Componentes', underline=0, command=self.emConstrucao)
        self.menuTopologia.add_command(label='Transformada da Distancia', underline=0, command=self.emConstrucao)
        self.menuTopologia.add_command(label='Esqueletizacao', underline=0, command=self.emConstrucao)
        self.menubar.add_cascade(label="Topologia", underline=0, menu=self.menuTopologia)

        # Grupo principal, onde serao atualizados os widgets
        self.grupoPrincipal = Frame(self.canvas, width=self.largura, height=self.altura, bd=1, padx=10, pady=10)
        self.grupoPrincipal.pack()
        #self.grupoPrincipal.grid_propagate(False) # Faz com que o Frame nao seja redimensionado com a mudanca dos widgets
        self.canvas.create_window((4,20), window=self.grupoPrincipal, anchor="nw", tags="self.grupoPrincipal")
        self.grupoPrincipal.bind("<Configure>", self.OnFrameConfigure)

    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onExit(self):
        self.parent.destroy()

    def limpaTela(self):
        for widget in self.grupoPrincipal.winfo_children():
            widget.destroy()

    def emConstrucao(self):
        tkm.showinfo(title="Em construcao", message="Recurso em Construcao...")

    def load_file(self, titulo, varFile, tipos):
        if os.path.isfile(varFile.get()):
            path = os.path.dirname(varFile.get())
            self.flopt['initialdir'] = path
        else:
            self.flopt['initialdir'] = os.path.curdir
        self.flopt['filetypes'] = tipos
        arquivo = tkf.askopenfilename(title=titulo, **self.flopt)
        if arquivo:
            varFile.set(arquivo)

    def widgetFile(self, master, titulo, texto, varFile, tuplaFiletype):
        esteFrame = LabelFrame(master, text=titulo, padx=5, pady=5)

        j = 0
        varFile.set("Nenhum arquivo informado")
        labelRotulo = Label(esteFrame, text=texto)
        labelRotulo.grid(row=j,column=0,sticky=cte.E)

        botao = Button(esteFrame, text="Procurar", command=lambda:self.load_file(texto, varFile, tuplaFiletype), width=10)
        botao.grid(row=j, column=1, pady=5,sticky=cte.W)

        j += 1

        labelArq = Label(esteFrame, textvariable=varFile, bg='white')
        labelArq.grid(row=j, column=0, columnspan=2)

        return esteFrame

    def refreshImg(self):
        try:
            self.grupoPrincipal.photo = ImageTk.PhotoImage(self.img.img)
            if hasattr(self.grupoPrincipal, 'canvas'):
                self.grupoPrincipal.canvas.destroy()
            self.grupoPrincipal.canvas = Canvas(self.grupoPrincipal)
            self.grupoPrincipal.canvas.create_image(0,0,image=self.grupoPrincipal.photo, anchor=cte.NW)
            self.grupoPrincipal.canvas.config(bg='white', width=self.img.altura, height=self.img.largura)
            #self.grupoPrincipal.canvas.place(x=self.parent.winfo_screenwidth()/2, y=self.parent.winfo_screenheight()/2, anchor=cte.CENTER)
            self.grupoPrincipal.canvas.place(x=0, y=0, anchor=cte.NW)
            self.grupoPrincipal.update_idletasks()
        except Exception as e:
            tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

#==============================================================================
#   Metodos relacionados ao meno Arquivo
#==============================================================================

    def abrir(self):
        try:
            self.limpaTela()
            self.load_file('Arquivos de Imagem', self.arqImg, self.tipos)
            self.img = Imagem(self.arqImg.get())
            self.refreshImg()
        except Exception as e:
            tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def saveFile(self):
        try:
            nome,extensao = os.path.splitext(self.arqImg.get())
            extensao = extensao.replace('.','')
            self.img.salva(self.arqImg.get(), self.formatos[extensao.lower()])
            tkm.showinfo('Sucesso', 'Arquivo %s salvo com sucesso' % os.path.basename(self.arqImg.get()))
        except Exception as e:
            tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def salvar(self):
        if self.arqImg.get() == '':
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto para ser salvo')
        else:
            try:
                self.saveFile()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def salvarComo(self):
        if self.arqImg.get() == '':
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto para ser salvo')
        else:
            try:
                if os.path.isfile(self.arqImg.get()):
                    path = os.path.dirname(self.arqImg.get())
                    self.flopt['initialdir'] = path
                else:
                    self.flopt['initialdir'] = os.path.curdir
                self.flopt['filetypes'] = self.tipos
                nomeArq = tkf.asksaveasfilename(title='Salvar imagem como...', **self.flopt)
                if nomeArq:
                    self.arqImg.set(nomeArq)
                    self.saveFile()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def fecharArquivo(self):
        if not hasattr(self.grupoPrincipal, 'canvas') or self.grupoPrincipal.canvas.find_all() == ():
            tkm.showwarning('Aviso', 'Nao ha imagens abertas')
        else:
            try:
                self.img = self.imgOld = None
                self.grupoPrincipal.canvas.delete('all')
                self.grupoPrincipal.update_idletasks()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

#==============================================================================
#  Metodos relacionados ao menu Editar
#==============================================================================

    def desfazer(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        elif self.imgOld is None:
            tkm.showwarning('Aviso', 'Impossivel Desfazer')
        else:
            try:
                temp = self.img
                self.img = self.imgOld
                self.imgOld = temp
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

#==============================================================================
#   Metodos relacionados ao menu Cores
#==============================================================================
    def mudaCor(self, metodo):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.img = cor.mudaCor(self.imgOld, metodo)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getLimiar(self):
        self.Limiar = int(self.escalaLimiar.get())

        self.w.destroy()
            

    def formBinaria(self):
        self.Limiar = None

        self.w = Toplevel(self)
        self.w.wm_title("Informar o Limiar")

        self.w.geometry("+%d+%d" % (self.winfo_rootx()+50, self.winfo_rooty()+50))
        self.w.focus_set()

        i = 0

        self.labelLimiar = Label(self.w, text='Limiar', width=25)
        self.labelLimiar.grid(row=i, column=0)
        self.escalaLimiar = Scale(self.w, from_=0, to=255, resolution=1, length=350, orient=cte.HORIZONTAL)
        self.escalaLimiar.set(1)
        self.escalaLimiar.grid(row=i, column=1)
        i+=1

        self.botaoLimiar = Button(self.w, text='Ok', command=self.getLimiar, width=10)
        self.botaoLimiar.grid(row=i, column=0, columnspan=2)

        self.w.grid()


    def binaria(self, metodo):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                if metodo == 'limiar':
                    self.formBinaria()
                    self.wait_window(self.w)
                    if self.Limiar is not None:
                        self.imgOld = self.img
                        self.img = cor.binaria(self.imgOld, metodo, int(self.Limiar))
                        self.refreshImg()
                else:
                    self.imgOld = self.img
                    self.img = cor.binaria(self.imgOld, metodo)
                    self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getFatoresBalanco(self):
        self.fatores = [float(self.escalaFatorR.get())]
        self.fatores.append(float(self.escalaFatorG.get()))
        self.fatores.append(float(self.escalaFatorB.get()))

        self.w.destroy()

    def formBalanco(self):
        self.fator = None
        self.fatores = None

        self.w = Toplevel(self)
        self.w.wm_title("Informar os fatores de ajuste")

        self.w.geometry("+%d+%d" % (self.winfo_rootx()+50, self.winfo_rooty()+50))
        self.w.focus_set()

        i = 0

        self.labelFatorR = Label(self.w, text='Ajuste em R', width=25)
        self.labelFatorR.grid(row=i, column=0)
        self.escalaFatorR = Scale(self.w, from_=0, to=2, resolution=0.05, length=350, orient=cte.HORIZONTAL)
        self.escalaFatorR.set(0.5)
        self.escalaFatorR.grid(row=i, column=1)
        i+=1

        self.labelFatorG = Label(self.w, text='Ajuste em G', width=25)
        self.labelFatorG.grid(row=i, column=0)
        self.escalaFatorG = Scale(self.w, from_=0, to=2, resolution=0.05, length=350, orient=cte.HORIZONTAL)
        self.escalaFatorG.set(0.5)
        self.escalaFatorG.grid(row=i, column=1)
        i+=1

        self.labelFatorB = Label(self.w, text='Ajuste em B', width=25)
        self.labelFatorB.grid(row=i, column=0)
        self.escalaFatorB = Scale(self.w, from_=0, to=2, resolution=0.05, length=350, orient=cte.HORIZONTAL)
        self.escalaFatorB.set(0.5)
        self.escalaFatorB.grid(row=i, column=1)
        i+=1

        self.botaoFator = Button(self.w, text='Ok', command=self.getFatoresBalanco, width=10)
        self.botaoFator.grid(row=i, column=0, columnspan=2)

        self.w.grid()

    def balancoCor(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.formBalanco()
                self.wait_window(self.w)
                if self.fatores is not None:
                    self.imgOld = self.img
                    self.img = cor.balanco(self.imgOld, self.fatores[0], self.fatores[1], self.fatores[2])
                    self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def halftoning(self, metodo='bayer2'):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                if metodo == 'bayer2':
                    self.img = cor.bayer(self.imgOld, 2)
                elif metodo == 'bayer5':
                    self.img = cor.bayer(self.imgOld, 5)
                elif metodo == 'floyd':
                    self.img = cor.floyd(self.imgOld)
                elif metodo == 'atkinson':
                    self.img = cor.atkinson(self.imgOld)
                else:
                    raise Exception('Metodo de halftoning desconhecido')
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getBilhoContraste(self):
        self.brilho = float(self.escalaBrilho.get())
        self.contraste = float(self.escalaContraste.get())

        self.w.destroy()
            

    def formBilhoContraste(self):
        self.brilho = None
        self.constraste = None

        self.w = Toplevel(self)
        self.w.wm_title("Informar os fatores de ajuste de brilho e contraste")

        self.w.geometry("+%d+%d" % (self.winfo_rootx()+50, self.winfo_rooty()+50))
        self.w.focus_set()

        i = 0

        self.labelBrilho = Label(self.w, text='Brilho', width=25)
        self.labelBrilho.grid(row=i, column=0)
        self.escalaBrilho = Scale(self.w, from_=-255, to=255, resolution=0.5, length=350, orient=cte.HORIZONTAL)
        self.escalaBrilho.set(0)
        self.escalaBrilho.grid(row=i, column=1)
        i+=1

        self.labelContraste = Label(self.w, text='Contraste', width=25)
        self.labelContraste.grid(row=i, column=0)
        self.escalaContraste = Scale(self.w, from_=-255, to=255, resolution=0.5, length=350, orient=cte.HORIZONTAL)
        self.escalaContraste.set(1)
        self.escalaContraste.grid(row=i, column=1)
        i+=1

        self.botaoBC = Button(self.w, text='Ok', command=self.getBilhoContraste, width=10)
        self.botaoBC.grid(row=i, column=0, columnspan=2)

        self.w.grid()

    def brilhoContraste(self, brilho=0.0, contraste=1.0):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.formBilhoContraste()
                self.wait_window(self.w)
                if self.brilho is not None and self.contraste is not None:
                    self.imgOld = self.img
                    self.img = cor.brilhoContraste(self.imgOld, self.brilho, self.contraste)
                    self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def alargamentoContraste(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.img = cor.alargamentoContraste(self.imgOld)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def equalizacaoHistograma(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.img = Imagem.equalizacaoHistograma(self.imgOld)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def visualizacaoHistogramas(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.imagem = cor.mudaCor(self.img, 'luminosity')
                Imagem.visualizacaoHistogramas(self.img, self.imagem)
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getRespostaSim(self):
        self.Resposta = 'sim'
        self.w.destroy()

    def getRespostaNao(self):
        self.Resposta = 'nao'
        self.w.destroy()

    def formEspecificacaoDiretaHistograma(self):
        self.Resposta = None

        self.w = Toplevel(self)
        self.w.wm_title("Conversão para tons de cinza")

        self.w.focus_set()

        self.labelCores = Label(self.w, text='Deseja que a segunda imagem seja convertida\n para tons de cinza?', width=40)
        self.labelCores.grid(row=0, column=0, columnspan=2)

        self.botaoBC = Button(self.w, text='Sim', command=self.getRespostaSim, width=10)
        self.botaoBC.grid(row=1, column=0, rowspan=2)

        self.botaoBC = Button(self.w, text='Não', command=self.getRespostaNao, width=10)
        self.botaoBC.grid(row=1, column=1, rowspan=2)

        self.w.grid()

    def especificacaoDiretaHistograma(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.load_file('Arquivos de Imagem', self.arqImg, self.tipos)
                self.imagem = Imagem(self.arqImg.get())
                self.formEspecificacaoDiretaHistograma()
                self.wait_window(self.w)
                if self.Resposta is not None:
                    self.imgOld = self.img
                    if self.Resposta == 'sim':
                        self.imagem = cor.mudaCor(self.img, 'luminosity')
                    else:
                        self.imagem = self.img
                    self.img = Imagem.especificacaoDiretaHistograma(self.imagem, self.imagem)
                    self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getRespostaProb(self):
        self.m = 'prob'

        self.nCores = int(self.escalaCores.get())

        self.w.destroy()

    def getRespostaUni(self):
        self.m = 'uniforme'

        self.nCores = int(self.escalaCores.get())

        self.w.destroy()

    def formQuantizacaoCores(self):
        self.nCores = None
        self.m = None

        self.w = Toplevel(self)
        self.w.wm_title("Quantização de cores")

        self.w.focus_set()

        self.labelCores = Label(self.w, text='Escolha o nível de intensidade e o método', width=40)
        self.labelCores.grid(row=0, column=0, columnspan=4)
        self.escalaCores = Scale(self.w, from_=0, to=255, resolution=1, length=350, orient=cte.HORIZONTAL)
        self.escalaCores.set(0)
        self.escalaCores.grid(row=1, column=0, columnspan=4)

        self.botaoBC = Button(self.w, text='Intervalos uniformes', command=self.getRespostaUni, width=15)
        self.botaoBC.grid(row=2, column=0, rowspan=2, columnspan=4)

        self.botaoD = Button(self.w, text='Distribuição de probabilidade', command=self.getRespostaProb, width=25)
        self.botaoD.grid(row=4, column=0, rowspan=2, columnspan=4)

        self.w.grid()

    def quantizacaoCores(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.formQuantizacaoCores()
                self.wait_window(self.w)
                if self.nCores is not None:
                    self.imgOld = self.img
                    self.img = cor.quantizacaoCores(self.imgOld, self.m, self.nCores)
                    self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getSalPimenta(self):
        self.porcentagem = float(self.escala2.get())
        self.proporcao = float(self.escala1.get())

        self.w.destroy()
            

    def formSalPimenta(self):
        self.porcentagem = None
        self.proporcao = None

        self.w = Toplevel(self)
        self.w.wm_title("Parâmetros do sal pimenta")

        self.w.geometry("+%d+%d" % (self.winfo_rootx()+50, self.winfo_rooty()+50))
        self.w.focus_set()

        i = 0

        self.label1 = Label(self.w, text='Proporção de ruído', width=25)
        self.label1.grid(row=i, column=0)
        self.escala1 = Scale(self.w, from_=0, to=1, resolution=0.01, length=350, orient=cte.HORIZONTAL)
        self.escala1.set(0.01)
        self.escala1.grid(row=i, column=1)
        i+=1

        self.label2 = Label(self.w, text='Porcentagem de sal', width=25)
        self.label2.grid(row=i, column=0)
        self.escala2 = Scale(self.w, from_=0, to=1, resolution=0.01, length=350, orient=cte.HORIZONTAL)
        self.escala2.set(0.5)
        self.escala2.grid(row=i, column=1)
        i+=1

        self.botaoBC = Button(self.w, text='Ok', command=self.getSalPimenta, width=10)
        self.botaoBC.grid(row=i, column=0, columnspan=2)

        self.w.grid()

    def salPimenta(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            self.formSalPimenta()
            self.wait_window(self.w)
            try:
                self.imgOld = self.img
                self.img = cor.salPimenta(self.imgOld)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def ruidoGaausiano(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.img = cor.ruidoGaausiano(self.imgOld)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def qnteArbitraria(self):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = cor.mudaCor(self.img, 'luminosity')
                self.img = cor.quantizacaoCores(self.imgOld, 'uniforme', 4)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))



#==============================================================================
#   Metodos relacionados ao menu Imagem
#==============================================================================
    def converte(self, modo='RGB'):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img.copia()
                self.img.converte(modo)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def info(self):
        if self.arqImg.get() == '':
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                texto = 'Imagem %s, modo: %s (%d x %d pixels)' % (self.img.img.format, self.img.img.mode, self.img.img.size[0], self.img.img.size[1])
                tkm.showinfo('Aviso', texto)
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def comparaImagens(self, metodo = 'rmse'):
        
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.load_file('Arquivos de Imagem', self.arqImg, self.tipos)
                self.imgOld = Imagem(self.arqImg.get())
                resultado = Imagem.comparaImagens(self.img, self.imgOld, metodo)
                if metodo == 'rmse':
                    tkm.showinfo(title='Raiz do Erro Médio Quadrático', message='O resultado dado pela Raiz do Erro Médio Quadrático é de: \n' + str(resultado))
                elif metodo == 'jaccard':
                    tkm.showinfo(title='Coeficiente de Jaccard', message='O resultado dado pelo Coeficiente de Jaccard é de: \n' + str(resultado))
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def filtragemEspacial(self, metodo = 'sobel'):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                if metodo == 'sobel':
                    self.imgOld = self.img
                    self.img = Imagem.sobel(self.imgOld)
                    self.refreshImg()
                elif metodo == 'laplace1':
                    self.imgOld = self.img
                    self.img = Imagem.laplace(self.imgOld, 1)
                    self.refreshImg()
                elif metodo == 'laplace2':
                    self.imgOld = self.img
                    self.img = Imagem.laplace(self.imgOld, 2)
                    self.refreshImg()
                elif metodo == 'laplace3':
                    self.imgOld = self.img
                    self.img = Imagem.laplace(self.imgOld, 3)
                    self.refreshImg()
                elif metodo == 'roberts':
                    self.imgOld = self.img
                    self.img = Imagem.roberts(self.imgOld)
                    self.refreshImg()
                elif metodo == 'prewitt':
                    self.imgOld = self.img
                    self.img = Imagem.prewitt(self.imgOld)
                    self.refreshImg()
                elif metodo == 'scharr':
                    self.imgOld = self.img
                    self.img = Imagem.scharr(self.imgOld)
                    self.refreshImg()
                elif metodo == 'linhas1':
                    self.imgOld = self.img
                    self.img = Imagem.linhas(self.imgOld, 1)
                    self.refreshImg()
                elif metodo == 'linhas2':
                    self.imgOld = self.img
                    self.img = Imagem.linhas(self.imgOld, 2)
                    self.refreshImg()
                elif metodo == 'linhas3':
                    self.imgOld = self.img
                    self.img = Imagem.linhas(self.imgOld, 3)
                    self.refreshImg()
                elif metodo == 'linhas4':
                    self.imgOld = self.img
                    self.img = Imagem.linhas(self.imgOld, 4)
                    self.refreshImg()
                elif metodo == 'linhas5':
                    self.imgOld = self.img
                    self.img = Imagem.linhas(self.imgOld, 5)
                    self.refreshImg()
                elif metodo == 'emboss':
                    self.imgOld = self.img
                    self.img = Imagem.emboss(self.imgOld)
                    self.refreshImg()
                elif metodo == 'agucamento4':
                    self.imgOld = self.img
                    self.img = Imagem.agucamento(self.imgOld, 4)
                    self.refreshImg()
                elif metodo == 'agucamento8':
                    self.imgOld = self.img
                    self.img = Imagem.agucamento(self.imgOld, 8)
                    self.refreshImg()
                elif metodo == 'relevo':
                    self.imgOld = self.img
                    self.img = Imagem.relevo(self.imgOld)
                    self.refreshImg()

            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))
    

    def getRespostaAlpha(self):
        self.alpha = float(self.escalaAlpha.get())

        self.w.destroy()

    def formAlpha(self):
        self.alpha = None

        self.w = Toplevel(self)
        self.w.wm_title("Escolha de alfa")

        self.w.focus_set()

        self.labelAlpha = Label(self.w, text='Escolha o parâmetro alfa', width=40)
        self.labelAlpha.grid(row=0, column=0, columnspan=4)
        self.escalaAlpha = Scale(self.w, from_=0, to=1, resolution=0.01, length=350, orient=cte.HORIZONTAL)
        self.escalaAlpha.set(0)
        self.escalaAlpha.grid(row=1, column=0, columnspan=4)
        
        self.botaoBC = Button(self.w, text='Ok', command=self.getRespostaAlpha, width=15)
        self.botaoBC.grid(row=2, column=0, rowspan=2, columnspan=4)

        self.w.grid()

    def getRespostaLmb(self):
        self.lmb = float(self.escalaLmb.get())

        self.w.destroy()

    def formLmb(self):
        self.lmb = None

        self.w = Toplevel(self)
        self.w.wm_title("Escolha de lâmbda")

        self.w.focus_set()

        self.labelLmb = Label(self.w, text='Escolha o parâmetro lâmbda', width=40)
        self.labelLmb.grid(row=0, column=0, columnspan=4)
        self.escalaLmb = Scale(self.w, from_=0, to=1, resolution=0.01, length=350, orient=cte.HORIZONTAL)
        self.escalaLmb.set(0)
        self.escalaLmb.grid(row=1, column=0, columnspan=4)
        
        self.botaoBC = Button(self.w, text='Ok', command=self.getRespostaLmb, width=15)
        self.botaoBC.grid(row=2, column=0, rowspan=2, columnspan=4)

        self.w.grid()

    def operacoesPP(self, metodo = 'soma'):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.load_file('Arquivos de Imagem', self.arqImg, self.tipos)
                self.imgOld = self.img
                self.imagem = Imagem(self.arqImg.get())
                if metodo == 'soma':
                    self.img = Imagem.soma(self.img, self.imagem)
                elif metodo == 'sub':
                    self.img = Imagem.subtracao(self.img, self.imagem)
                elif metodo == 'mult':
                    self.img = Imagem.multiplicacao(self.img, self.imagem)
                elif metodo == 'div':
                    self.img = Imagem.divisao(self.img, self.imagem)
                elif metodo == 'combmenor':
                    imagem1 = cor.mudaCor(self.img, 'luminosity')
                    imagem2 = cor.mudaCor(self.imagem, 'luminosity')
                    self.img = Imagem.combinacaoMenor(self.img, self.imagem, imagem1, imagem2)
                elif metodo == 'combmaior':
                    imagem1 = cor.mudaCor(self.img, 'luminosity')
                    imagem2 = cor.mudaCor(self.imagem, 'luminosity')
                    self.img = Imagem.combinacaoMaior(self.img, self.imagem, imagem1, imagem2)
                elif metodo == 'comblinear':
                    self.formAlpha()
                    self.wait_window(self.w)
                    self.img = Imagem.combinacaoLinear(self.img, self.imagem, self.alpha)
                elif metodo == 'combsigmoideX':
                    self.formLmb()
                    self.wait_window(self.w)
                    self.img = Imagem.combinacaoSigmoide(self.img, self.imagem, 1 , self.lmb)
                elif metodo == 'combsigmoideY':
                    self.formLmb()
                    self.wait_window(self.w)
                    self.img = Imagem.combinacaoSigmoide(self.img, self.imagem, 2 , self.lmb)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def getRespostaRaio(self):
        self.raio = int(self.escalaRaio.get())

        self.w.destroy()

    def formRaio(self):
        self.raio = None

        self.w = Toplevel(self)
        self.w.wm_title("Escolha do raio")

        self.w.focus_set()

        self.labelRaio = Label(self.w, text='Escolha o raio da máscara', width=40)
        self.labelRaio.grid(row=0, column=0, columnspan=4)
        self.escalaRaio = Scale(self.w, from_=1, to=255, resolution=1, length=350, orient=cte.HORIZONTAL)
        self.escalaRaio.set(0)
        self.escalaRaio.grid(row=1, column=0, columnspan=4)
        
        self.botaoBC = Button(self.w, text='Ok', command=self.getRespostaRaio, width=15)
        self.botaoBC.grid(row=2, column=0, rowspan=2, columnspan=4)

        self.w.grid()

    def formBloco(self):
        self.raio = None

        self.w = Toplevel(self)
        self.w.wm_title("Escolha do tamanho do bloco")

        self.w.focus_set()

        self.labelRaio = Label(self.w, text='Escolha o tamanho do bloco', width=40)
        self.labelRaio.grid(row=0, column=0, columnspan=4)
        self.escalaRaio = Scale(self.w, from_=1, to=255, resolution=1, length=350, orient=cte.HORIZONTAL)
        self.escalaRaio.set(0)
        self.escalaRaio.grid(row=1, column=0, columnspan=4)
        
        self.botaoBC = Button(self.w, text='Ok', command=self.getRespostaRaio, width=15)
        self.botaoBC.grid(row=2, column=0, rowspan=2, columnspan=4)

        self.w.grid()

    def suavicacao(self, metodo = 'media'):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.formRaio()
                self.wait_window(self.w)

                if metodo == 'conservativa':
                    nova = cor.mudaCor(self.img, 'luminosity')
                    self.img = Imagem.suavizacao(self.img, 'conservativa', self.raio, nova)
                else:
                    self.img = Imagem.suavizacao(self.img, metodo, self.raio)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def espaciais(self, metodo = 'erosao'):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                if metodo == 'pixelizacao':
                    self.formBloco()
                    self.wait_window(self.w)
                    self.img = Imagem.espaciais(self.img, metodo, self.raio)
                else:
                    self.formRaio()
                    self.wait_window(self.w)
                    self.img = Imagem.espaciais(self.img, metodo, self.raio)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

    def frequencia(self, metodo):
        if self.arqImg.get() == '' or self.img is None:
            tkm.showwarning('Aviso', 'Nao ha arquivo aberto')
        else:
            try:
                self.imgOld = self.img
                self.img = Imagem.frequencia(self.img, metodo)
                self.refreshImg()
            except Exception as e:
                tkm.showerror('Erro', 'O seguinte erro ocorreu: %s' % str(e.args))

# Cria janela principal
top = Tk()
top.title("PhotoPobre Beta v1.0")
# Maximiza
w,h = top.winfo_screenwidth(), top.winfo_screenheight()
top.geometry("%dx%d+0+0" % (w,h))

# Executa em loop ate janela ser fechada
mainw = Gui(parent=top)
mainw.mainloop()

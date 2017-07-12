# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 17:54:51 2016

@author: marcos
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import math
import random
from scipy.fftpack import fftshift, ifftshift, fftn, ifftn

#==============================================================================
# Classe Imagem: encapsula objeto Image, do modulo PIL
#   pode ser instanciada com um nome de arquivo ja existente ou com uma tupla
#       contendo 2 inteiros correspondendo as dimensoes (altura x largura) da imagem a ser criada
#==============================================================================

class Imagem(object):

#==============================================================================
#   Construtor e metodos internos essenciais
#==============================================================================
    def __init__(self, entrada):
        self.initVars()

        try:
            if type(entrada) is str:
                self.img = Image.open(entrada)
                self.altura, self.largura = self.img.size
            elif type(entrada) is tuple:
                self.img = Image.new('RGB', entrada)
                self.altura = int(entrada[0])
                self.largura = int(entrada[1])
            else:
                raise Exception('Voce deve especificar um arquivo ou um tamanho para a imagem.')
        except Exception as e:
            raise Exception(e.args)

    # Inicializacao de flags
    def initVars(self):
        self._y = 0
        self._getSet = False

#==============================================================================
# Metodos essenciais de uso externo
#==============================================================================

    # Salvamento de imagem em disco
    def salva(self, arquivo, formato='png'):
        try:
            self.img.save(arquivo, formato)
            self.img = Image.open(arquivo)
        except Exception as e:
            raise Exception(e.args)

    # Converte imagem para outro modo
    def converte(self, modo='RGB'):
        try:
            self.img = self.img.convert(modo)
        except Exception as e:
            raise Exception(e.args)

    # Exibe imagem em tela
    def exibe(self):
        try:
            self.img.show()
        except Exception as e:
            raise Exception(e.args)

    # Copia imagem
    def copia(self):
        try:
            img2 = Imagem((self.altura, self.largura))
            img2.img = self.img.copy()
            return img2
        except Exception as e:
            raise Exception(e.args)

    # Obtem array de dados apenas com numeros inteiros
    def arr(self):
        try:
            dados = np.empty((self.altura, self.largura, 3), dtype=int)
            for i in range(self.altura):
                for j in range(self.largura):
                    r,g,b = self.img.getpixel((i, j))
                    dados[i][j] = np.array([r,g,b])
            return dados
        except Exception as e:
            raise Exception(e.args)

    # Obtem array de dados linear (numeros inteiros apenas) com a lista de pixels
    def arrLin(self):
        try:
            dados = np.empty((self.altura * self.largura, 3), dtype=int)
            k = 0
            for i in range(self.altura):
                for j in range(self.largura):
                    r,g,b = self.img.getpixel((i, j))
                    dados[k] = np.array([r,g,b])
                    k += 1
            return dados
        except Exception as e:
            raise Exception(e.args)
            
    # Obtem array de dados linear (numeros inteiros apenas) com as coordenada agregadas
    def arrLinGeo(self):
        try:
            dados = np.empty((self.altura * self.largura, 3), dtype=int)
            k = 0
            for i in range(self.altura):
                for j in range(self.largura):
                    r,g,b = self.img.getpixel((i, j))
                    if r != g or r != b or g != b:
                        Y = int(0.299*r + 0.587*g + 0.114*b)
                    else:
                        Y = r
                    dados[k] = np.array([i,j,Y])
                    k += 1
            return dados
        except Exception as e:
            raise Exception(e.args)

#==============================================================================
#   Metodos para manipulacao da matriz
#==============================================================================

    # Obtencao de pixel da imagem (aceita notacao [i][j] ou [i,j])
    def __getitem__(self, indices):
        if type(indices) is tuple:
            i, j = indices
            if type(i) is not int or type(j) is not int:
                raise Exception('Os indices devem ser inteiros ou uma tupla de inteiros')
            return self.img.getpixel((i, j))
        elif type(indices) is int:
            if not self._getSet:
                self._getSet = True
                self._y = indices
                return self
            else:
                i = self._y
                self.initVars()
                return self.img.getpixel((i, indices))
        else:
            raise Exception('Os indices devem ser inteiros ou uma tupla de inteiros')

    # Altera ou define pixel da imagem (aceita notacao [i][j] ou [i,j]). Aceita passagem de uma tupla de inteiros rgb
    def __setitem__(self, indices, px):
        if type(px) is tuple:
            if len(px) != 3:
                raise Exception('A tupla deve ter dimensao 3')

            try:
                pix = tuple([min(255, max(int(x),0)) for x in px])
            except:
                raise Exception('Os elementos da tupla devem ser todos inteiros ou float. Problema em (%s,%s,%s)' % px)
        else:
            raise Exception('Os valores RGB devem ser passados em uma tupla')

        if type(indices) is tuple:
            i, j = indices
            if type(i) is not int or type(j) is not int:
                raise Exception('Os indices devem ser inteiros ou uma tupla de inteiros.')

            try:
                self.img.putpixel((i, j), pix)
            except Exception as e:
                raise Exception(e.args)

        elif type(indices) is int:
            if not self._getSet:
                self._getSet = True
                self._y = indices
                return self
            else:
                i = self._y
                self.initVars()
                try:
                    self.img.putpixel((i, indices), pix)
                except Exception as e:
                    raise Exception(e.args)
        else:
            raise Exception('Os indices devem ser inteiros ou uma tupla de inteiros.')

#==============================================================================
#   Metodos para operacoes com imagens e valores numericos
#==============================================================================

    # Soma: Imagem = Imagem + Imagem
    # Se: Imagem = Imagem + valor, chama o metodo addNum
    def __add__(self, outra):
        if not isinstance(outra, Imagem) and type(outra) is not int and type(outra) is not float:
            raise Exception('Uma imagem soh pode ser somada a outra imagem ou a um numero.')

        if type(outra) is float or type(outra) is int:
            # se outra for numerico, chama o metodo addNum
            return self.addNum(outra)
        elif self.altura != outra.altura or self.largura != outra.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes para serem somadas.')

        try:
            nova = Imagem((self.altura, self.largura))
            nova.img = self.img.copy()

            for i in range(self.altura):
                for j in range(self.largura):
                    nova[i][j] = tuple([min(255, max(0,i)) for i in np.array(self.img.getpixel((i, j))) + np.array(outra.img.getpixel((i, j)))])

            return nova
        except Exception as e:
            raise Exception(e.args)

    # Soma: Imagem = Imagem + numero
    def addNum(self, valor):
        try:
            nova = Imagem((self.altura, self.largura))
            nova.img = self.img.copy()

            for i in range(self.altura):
                for j in range(self.largura):
                    nova[i][j] = tuple([min(255, max(0,i)) for i in np.array(self.img.getpixel((i, j))) + valor])

            return nova
        except Exception as e:
            raise Exception(e.args)

    # Subtracao: Imagem = Imagem - Imagem
    # Se: Imagem = Imagem - valor, chama o metodo subNum
    def __sub__(self, outra):
        if not isinstance(outra, Imagem) and type(outra) is not int and type(outra) is not float:
            raise Exception('Uma imagem soh pode ser somada a outra imagem ou a um numero.')

        if type(outra) is float or type(outra) is int:
            # se outra for numerico, chama o metodo subNum
            return self.subNum(outra)
        elif self.altura != outra.altura or self.largura != outra.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes para serem subtraídas.')

        try:
            nova = Imagem((self.altura, self.largura))
            nova.img = self.img.copy()

            for i in range(self.altura):
                for j in range(self.largura):
                    nova[i][j] = tuple([min(255, max(0,i)) for i in np.array(self.img.getpixel((i, j))) - np.array(outra.img.getpixel((i, j)))])

            return nova
        except Exception as e:
            raise Exception(e.args)

    # Subtracao: Imagem = Imagem - numero
    def subNum(self, valor):
        try:
            nova = Imagem((self.altura, self.largura))
            nova.img = self.img.copy()

            for i in range(self.altura):
                for j in range(self.largura):
                    nova[i][j] = tuple([min(255, max(0,i)) for i in np.array(self.img.getpixel((i, j))) - valor])

            return nova
        except Exception as e:
            raise Exception(e.args)
        
    # Multiplicacao: Imagem = Imagem * Imagem
    # Multiplicacao: Imagem = Imagem * numero chama multNum
    def __mul__(self, outra):
        if not isinstance(outra, Imagem) and type(outra) is not int and type(outra) is not float:
            raise Exception('Uma imagem soh pode ser somada a outra imagem ou a um numero.')

        if type(outra) is float or type(outra) is int:
            # se outra for numerico, chama o metodo subNum
            return self.multNum(outra)
        elif self.altura != outra.altura or self.largura != outra.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes para serem subtraídas.')

        try:
            nova = Imagem((self.altura, self.largura))

            auxR = np.zeros((self.altura, self.largura), dtype = float)
            auxG = np.zeros((self.altura, self.largura), dtype = float)
            auxB = np.zeros((self.altura, self.largura), dtype = float)

            #Normalizar a segunda imagem
            minR = 100000
            minG = 100000
            minB = 100000
            maxR = -1
            maxG = -1
            maxB = -1

            for i in range(self.altura):
                for j in range(self.largura):
                    r, g, b = outra.img.getpixel((i, j))
                    if r < minR:
                        minR = r
                    if g < minG:
                        minG = g
                    if b < minB:
                        minB = b
                    if r > maxR:
                        maxR = r
                    if g > maxG:
                        maxG = g
                    if b > maxB:
                        maxB = b

            for i in range(self.altura):
                for j in range(self.largura):
                    r, g, b = outra.img.getpixel((i, j))
                    r = float((float(r) - minR) / (maxR - minR))
                    g = float((float(g) - minG) / (maxG - minG))
                    b = float((float(b) - minB) / (maxB - minB))
                    auxR[i][j] = r
                    auxG[i][j] = g
                    auxB[i][j] = b

            for i in range(self.altura):
                for j in range(self.largura):
                    r = auxR[i][j]
                    g = auxG[i][j]
                    b = auxB[i][j] 
                    r1, g1, b1 = self.img.getpixel((i, j))


                    nova[i][j] = (min(255, r*r1), min(255, g*g1), min(255, b*b1))
            return nova
        except Exception as e:
            raise Exception(e.args)

    def multNum(self, valor):
        try:
            nova = Imagem((self.altura, self.largura))
            nova.img = self.img.copy()
            for i in range(self.altura):
                for j in range(self.largura):
                    nova[i][j] = tuple([min(255, max(0,i)) for i in np.array(self.img.getpixel((i, j))) * valor])

            return nova
        except Exception as e:
            raise Exception(e.args)

    # Divisao: Imagem = Imagem / Imagem
    # Divisao: Imagem = Imagem / numero chama divNum
    def __truediv__(self, outra):
        if not isinstance(outra, Imagem) and type(outra) is not int and type(outra) is not float:
            raise Exception('Uma imagem soh pode ser somada a outra imagem ou a um numero.')

        if type(outra) is float or type(outra) is int:
            # se outra for numerico, chama o metodo subNum
            return self.divNum(outra)
        elif self.altura != outra.altura or self.largura != outra.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes para serem subtraídas.')

        try:
            nova = Imagem((self.altura, self.largura))
            
            auxR = np.zeros((self.altura, self.largura), dtype = float)
            auxG = np.zeros((self.altura, self.largura), dtype = float)
            auxB = np.zeros((self.altura, self.largura), dtype = float)
            
            #Normalizar a segunda imagem
            minR = 100000
            minG = 100000
            minB = 100000
            maxR = -1
            maxG = -1
            maxB = -1

            for i in range(self.altura):
                for j in range(self.largura):
                    r, g, b = outra.img.getpixel((i, j))
                    if r < minR:
                        minR = r
                    if g < minG:
                        minG = g
                    if b < minB:
                        minB = b
                    if r > maxR:
                        maxR = r
                    if g > maxG:
                        maxG = g
                    if b > maxB:
                        maxB = b

            for i in range(self.altura):
                for j in range(self.largura):
                    r, g, b = outra.img.getpixel((i, j))
                    r = float((float(r) - minR) / (maxR - minR))
                    g = float((float(g) - minG) / (maxG - minG))
                    b = float((float(b) - minB) / (maxB - minB))
                    auxR[i][j] = r
                    auxG[i][j] = g
                    auxB[i][j] = b

            for i in range(self.altura):
                for j in range(self.largura):
                    r = auxR[i][j]
                    g = auxG[i][j]
                    b = auxB[i][j] 
                    r1, g1, b1 = self.img.getpixel((i, j))

                    if r == 0.0:
                        r = 255
                    else:
                        r = r1 / r
                    if g == 0.0:
                        g = 255
                    else:
                        g = g1 / g
                    if b == 0.0:
                        b = 255
                    else:
                        b = b1 / b

                    nova[i][j] = (r, g, b)

            return nova
        except Exception as e:
            raise Exception(e.args)

    def divNum(self, valor):
        try:
            nova = Imagem((self.altura, self.largura))
            nova.img = self.img.copy()
            for i in range(self.altura):
                for j in range(self.largura):
                    nova[i][j] = tuple([min(255, max(0,i)) for i in np.array(self.img.getpixel((i, j))) // valor])

            return nova
        except Exception as e:
            raise Exception(e.args)
        

#==============================================================================
#   Convolucao generica
#==============================================================================
    # Convolucao por gabarito truncado retorna um array de valores, nao uma imagem
    #  o resultado de uma convolucao pode ser combinado com o de outra (vide Sobel)
    #  sendo assim, os valores devem ser limitados no intervalo [0,255] somente ao termino
    #  da aplicacao dos operadores de convolucao. Para tal, utilizar o metodo getFromArray
    def convolucao(self, mascara):
        altMasc = mascara.shape[0]
        largMasc = mascara.shape[1]

        if altMasc != largMasc:
            raise Exception('A altura e a largura da mascara de convolucao devem ter a mesma dimensao')

        try:
            novosDados = np.empty((self.altura, self.largura, 3))

            if altMasc % 2 != 0: # Mascara de organizacao impar (resultado no centro)
                raio = altMasc // 2
                for y in range(self.altura):
                    for x in range(self.largura):
                        novosDados[y][x] = np.asarray([0,0,0])
                        a = 0
                        for i in range(max(0,y-raio), min(self.altura,y+raio+1)):
                            b = 0
                            for j in range(max(0,x-raio), min(self.largura,x+raio+1)):
                                novosDados[y][x] += np.array(self.img.getpixel((i, j))) * mascara[a][b]
                                b += 1
                            a += 1
            else: # Mascara de organizacao par (resultado no primeiro pixel)
                for y in range(self.altura):
                    for x in range(self.largura):
                        novosDados[y][x] = np.asarray([0,0,0])
                        a = 0
                        for i in range(y, min(self.altura,y+altMasc)):
                            b = 0
                            for j in range(x, min(self.largura, x+altMasc)):
                                novosDados[y][x] += np.array(self.img.getpixel((i, j))) * mascara[a][b]
                                b += 1
                            a += 1

            return novosDados
        except Exception as e:
            raise Exception(e.args)

    def roberts(self):
        a1 = self.convolucao(np.array([[1, 0], [0, -1]]))
        a2 = self.convolucao(np.array([[0, 1], [-1, 0]]))

        img1 = Imagem((self.altura, self.largura))
        img2 = Imagem((self.altura, self.largura))
        nova = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        img2 = self.getFromArray(a2)
        
        for y in range(self.altura):
            for x in range(self.largura):
                r, g, b = img1.img.getpixel((y, x))
                r1, g1, b1 = img2.img.getpixel((y, x))
                r = min(255, (r**2 + r1**2)**(0.5))
                g = min(255, (g**2 + g1**2)**(0.5))
                b = min(255, (b**2 + b1**2)**(0.5))

                nova[y][x] = (r, g, b)

        return nova
    
    def prewitt(self):
        a1 = self.convolucao(np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]]))
        a2 = self.convolucao(np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]))
        
        img1 = Imagem((self.altura, self.largura))
        img2 = Imagem((self.altura, self.largura))
        nova = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        img2 = self.getFromArray(a2)
        
        for y in range(self.altura):
            for x in range(self.largura):
                r, g, b = img1.img.getpixel((y, x))
                r1, g1, b1 = img2.img.getpixel((y, x))
                r = min(255, (r**2 + r1**2)**(0.5))
                g = min(255, (g**2 + g1**2)**(0.5))
                b = min(255, (b**2 + b1**2)**(0.5))

                nova[y][x] = (r, g, b)

        return nova

    def sobel(self):
        a1 = self.convolucao(np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]))
        a2 = self.convolucao(np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]))
        
        img1 = Imagem((self.altura, self.largura))
        img2 = Imagem((self.altura, self.largura))
        nova = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        img2 = self.getFromArray(a2)
        
        for y in range(self.altura):
            for x in range(self.largura):
                r, g, b = img1.img.getpixel((y, x))
                r1, g1, b1 = img2.img.getpixel((y, x))
                r = min(255, (r**2 + r1**2)**(0.5))
                g = min(255, (g**2 + g1**2)**(0.5))
                b = min(255, (b**2 + b1**2)**(0.5))

                nova[y][x] = (r, g, b)

        return nova
    
    def laplace(self, metodo = 1):
        
        if metodo == 1:
            a1 = self.convolucao(np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]))
            a2 = self.convolucao(np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]]))
        elif metodo == 2:
            a1 = self.convolucao(np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]]))
            a2 = self.convolucao(np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]))
        else:
            a1 = self.convolucao(np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
            a2 = self.convolucao(np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))

        img1 = Imagem((self.altura, self.largura))
        img2 = Imagem((self.altura, self.largura))
        nova = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        img2 = self.getFromArray(a2)
        
        for y in range(self.altura):
            for x in range(self.largura):
                r, g, b = img1.img.getpixel((y, x))
                r1, g1, b1 = img2.img.getpixel((y, x))
                r = min(255, r + r1)
                g = min(255, g + g1)
                b = min(255, b + b1)

                nova[y][x] = (r, g, b)

        return nova

    def scharr(self):
        a1 = self.convolucao(np.array([[3, 10, 3], [0, 0, 0], [-3, -10, -3]]))
        a2 = self.convolucao(np.array([[3, 0, -3], [10, 0, -10], [3, 0 , -3]]))
        
        img1 = Imagem((self.altura, self.largura))
        img2 = Imagem((self.altura, self.largura))
        nova = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        img2 = self.getFromArray(a2)
        
        for y in range(self.altura):
            for x in range(self.largura):
                r, g, b = img1.img.getpixel((y, x))
                r1, g1, b1 = img2.img.getpixel((y, x))
                r = min(255, (r**2 + r1**2)**(0.5))
                g = min(255, (g**2 + g1**2)**(0.5))
                b = min(255, (b**2 + b1**2)**(0.5))

                nova[y][x] = (r, g, b)

        return nova

    def linhas(self, metodo = 5):
        #Horizontal
        if metodo == 1:
            a1 = self.convolucao(np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]]))
            
            img1 = Imagem((self.altura, self.largura))
        
            img1 = self.getFromArray(a1)    

            return img1

        #Vertical
        elif metodo == 2:
            a2 = self.convolucao(np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]]))
                   
            img1 = Imagem((self.altura, self.largura))
        
            img1 = self.getFromArray(a2)    

            return img1

        #45 graus
        elif metodo == 3:
            a3 = self.convolucao(np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]]))

            img1 = Imagem((self.altura, self.largura))
        
            img1 = self.getFromArray(a3)    

            return img1

        #-45graus
        elif metodo == 4:
            a4 = self.convolucao(np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]]))

            img1 = Imagem((self.altura, self.largura))
        
            img1 = self.getFromArray(a4)

            return img1    

        else:
            a1 = self.convolucao(np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]]))
            a2 = self.convolucao(np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]]))
            a3 = self.convolucao(np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]]))
            a4 = self.convolucao(np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]]))
            
            img1 = Imagem((self.altura, self.largura))
            img2 = Imagem((self.altura, self.largura))
            img3 = Imagem((self.altura, self.largura))
            img4 = Imagem((self.altura, self.largura))
            nova = Imagem((self.altura, self.largura))
            
            img1 = self.getFromArray(a1)
            img2 = self.getFromArray(a2)
            img3 = self.getFromArray(a3)
            img4 = self.getFromArray(a4)
            
            for y in range(self.altura):
                for x in range(self.largura):
                    r, g, b = img1.img.getpixel((y, x))
                    r1, g1, b1 = img2.img.getpixel((y, x))
                    r2, g2, b2 = img3.img.getpixel((y, x))
                    r3, g3, b3 = img4.img.getpixel((y, x))

                    r = min(255, (r**2 + r1**2 + r2**2 + r3**2)**(0.5))
                    g = min(255, (g**2 + g1**2 + g2**2 + g3**2)**(0.5))
                    b = min(255, (b**2 + b1**2 + b2**2 + b3**2)**(0.5))

                    nova[y][x] = (r, g, b)

            return nova
    
    def emboss(self):
        a1 = self.convolucao(np.array([[-1, -1, 0], [-1, 0, 1], [0, 1, 1]]))
        
        img1 = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        
        return img1

    def agucamento(self, vizinhanca = 4):
        if vizinhanca == 4:
            a1 = self.convolucao(np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
            
            img1 = Imagem((self.altura, self.largura))
            
            img1 = self.getFromArray(a1)
            
            return img1
        else:
            a1 = self.convolucao(np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
            
            img1 = Imagem((self.altura, self.largura))
            
            img1 = self.getFromArray(a1)
            
            return img1

    def relevo(self):
        a1 = self.convolucao(np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]))
        
        img1 = Imagem((self.altura, self.largura))
        
        img1 = self.getFromArray(a1)
        
        return img1

    def getFromArray(self, arr):
        try:
            nova = Imagem((arr.shape[0], arr.shape[1]))
            for y in range(nova.altura):
                for x in range(nova.largura):
                    nova[y][x] = (arr[y][x][0], arr[y][x][1], arr[y][x][2])

            return nova
        except Exception as e:
            raise Exception(e.args)


#==============================================================================
#   Metodos estatisticos
#==============================================================================
    # Retorna o pixel (e posicao do mesmo) mais proximo do branco
    def maximo(self):
        branco = np.array([255, 255, 255])

        minDist = np.linalg.norm(branco)
        minPx = np.copy(branco)
        iMin = 0
        jMin = 0
        try:
            for i in range(self.altura):
                for j in range(self.largura):
                    d = np.linalg.norm(np.array(self.img.getpixel((i, j))) - branco)
                    if d <= minDist:
                        minDist = d
                        minPx = np.copy(np.array(self.img.getpixel((i, j))))
                        iMin = i
                        jMin = j
            return minPx, iMin, jMin
        except Exception as e:
            raise Exception(e.args)

    # Retorna o pixel (e posicao do mesmo) mais proximo do preto
    def minimo(self):
        preto = np.array([0, 0, 0])

        minDist = np.linalg.norm(np.array([255, 255, 255]))
        minPx = np.copy(preto)
        iMin = 0
        jMin = 0
        try:
            for i in range(self.altura):
                for j in range(self.largura):
                    d = np.linalg.norm(np.array(self.img.getpixel((i, j))) - preto)
                    if d <= minDist:
                        minDist = d
                        minPx = np.copy(np.array(self.img.getpixel((i, j))))
                        iMin = i
                        jMin = j
            return minPx, iMin, jMin
        except Exception as e:
            raise Exception(e.args)

    # Retorna os histogramas RGB da imagem
    def histogramas(self):
        hr = np.zeros(256, dtype=int)
        hg = np.zeros(256, dtype=int)
        hb = np.zeros(256, dtype=int)

        try:
            for i in range(self.altura):
                for j in range(self.largura):
                    r,g,b = self.img.getpixel((i, j))
                    hr[r] += 1
                    hg[g] += 1
                    hb[b] += 1
            return hr, hg, hb
        except Exception as e:
            raise Exception(e.args)

    # Retorna o histograma da versao cinza da imagem
    def histograma(self):
        h = np.zeros(256, dtype=int)

        try:
            for i in range(self.altura):
                for j in range(self.largura):
                    r,g,b = self.img.getpixel((i, j))
                    Y = int(0.299*r + 0.587*g + 0.114*b)
                    h[Y] += 1
            return h
        except Exception as e:
            raise Exception(e.args)

    #Calcula a cdf da imagem. Se a img não for RGB, a cdf se acumula na componente R
    #Recebe a imagem e os 3 histogramas de probabilidade
    def cdf(self, hr, hg=np.zeros(256), hb=np.zeros(256)):
        sigmaR = np.zeros(256, dtype=float)
        sigmaG = np.zeros(256, dtype=float)
        sigmaB = np.zeros(256, dtype=float)

        sigmaR[0] = hr[0]
        sigmaG[0] = hg[0]
        sigmaB[0] = hb[0]

        for i in range(1, 256):
            sigmaR[i] = sigmaR[i-1] + hr[i]
            sigmaG[i] = sigmaG[i-1] + hg[i]
            sigmaB[i] = sigmaB[i-1] + hb[i]

        return sigmaR, sigmaG, sigmaB

    #Equalização de histograma  
    def equalizacaoHistograma(self):
        nova = Imagem((self.altura, self.largura))

        hr, hg, hb = self.histogramas()

        hr = hr / (self.altura * self.largura)
        hg = hg / (self.altura * self.largura)
        hb = hb / (self.altura * self.largura)

        sigmaR, sigmaG, sigmaB = self.cdf(hr, hg, hb)

        sr = np.zeros(256, dtype=int)
        sg = np.zeros(256, dtype=int)
        sb = np.zeros(256, dtype=int)

        for k in range(256):

            sr[k] = round(255 * sigmaR[k])
            sg[k] = round(255 * sigmaG[k])
            sb[k] = round(255 * sigmaB[k])
        
        
        for i in range (self.altura):
            for j in range (self.largura):
                r, g, b = self.img.getpixel((i, j))
                nova[i][j] = (sr[r], sg[g], sb[b])

        return nova

    def visualizacaoHistogramas(self, imagem):
        #Histograma e cdf para RGB
        hr, hg, hb = self.histogramas()
        tam = self.altura * self.largura
        sigmaR, sigmaG, sigmaB = self.cdf(hr/tam, hg/tam, hb/tam)

        
        #Histograma e cdf para img monocromática (luminosity)
        h = imagem.histograma()

        #Apenas o cdf1 utilizado (imagem não é rgb)
        cdf1, cdf2, cdf3 = self.cdf(h/tam, h/tam, h/tam)

        #Plota o histograma de cada componente RGB

        intervalo = [i for i in range(0,256)]
        x = np.array(intervalo)
        
        fig, (axR, axG, axB, axP) = plt.subplots(ncols=4, figsize=(12, 8))
        axR.fill_between(x, hr)
        axR.set_title('Componente R')

        axG.fill_between(x, hg)
        axG.set_title('Componente G')

        axB.fill_between(x, hb)
        axB.set_title('Componente B')

        axP.fill_between(x, h)
        axP.set_title('Geral')

        fig.tight_layout()
        plt.show()

        #Histograma cdf
        
        fig, (axR, axG, axB, axP) = plt.subplots(ncols=4, figsize=(12, 8))
        axR.fill_between(x, sigmaR)
        axR.set_title('CDF R')

        axG.fill_between(x, sigmaG)
        axG.set_title('CDF G')

        axB.fill_between(x, sigmaB)
        axB.set_title('CDF B')

        axP.fill_between(x, cdf1)
        axP.set_title('CDF Geral')

        fig.tight_layout()
        plt.show()


    def especificacaoDiretaHistograma(self, imagem):
        nova = Imagem((self.altura, self.largura))
        hr, hg, hb = self.histogramas()
        HR, HG, HB = imagem.histogramas()

        hr = hr / (self.altura * self.largura)
        hg = hg / (self.altura * self.largura)
        hb = hb / (self.altura * self.largura)
        HR = HR / (imagem.altura * imagem.largura)
        HG = HG / (imagem.altura * imagem.largura)
        HB = HB / (imagem.altura * imagem.largura)

        sr = np.zeros(256, dtype=float)
        sg = np.zeros(256, dtype=float)
        sb = np.zeros(256, dtype=float)
        SR = np.zeros(256, dtype=float)
        SG = np.zeros(256, dtype=float)
        SB = np.zeros(256, dtype=float)

        sr, sg, sb = self.cdf(hr, hg, hb)
        SR, SG, SB = self.cdf(HR, HG, HB)

        for i in range (self.altura):
            for j in range (self.largura):
                r, g, b = self.img.getpixel((i, j))
                pr = sr[r]
                pg = sg[g]
                pb = sb[b]
                minR = 1000000
                minG = 1000000
                minB = 1000000
                kr = kg = kb = 0
                for k in range(256):
                    if abs(pr - SR[k]) < minR:
                        minR = abs(pr - SR[k])
                        kr = k
                    if abs(pg - SG[k]) < minG:
                        minG = abs(pg - SG[k])
                        kg = k
                    if abs(pb - SB[k]) < minB:
                        minB = abs(pb - SB[k])
                        kb = k

                nova[i][j] = (kr, kg, kb)
        
        return nova
        
    def comparaImagens(self, imagem, metodo):

        if metodo == 'jaccard':
    
            jaccard = 0.0
            
            for i in range(self.altura):
                for j in range(self.largura):
                    if self.img.getpixel((i, j)) == imagem.img.getpixel((i, j)):
                        jaccard += 1.0
        
            jaccard = jaccard / (self.altura * self.largura)
            return jaccard

        elif metodo == 'rmse':
            soma = 0.0
            for i in range(self.altura):
                for j in range(self.largura):

                    r, g, b = self.img.getpixel((i, j))
                    r1, g1, b1 = imagem.img.getpixel((i, j))

                    x = np.array([r, g, b])
                    x1 = np.array([r1, g1, b1])
                    
                    soma += ((np.linalg.norm(x-x1))**2)
                    
            soma = soma / (self.altura * self.largura)
            soma = soma**(0.5)
            return soma
        
    def soma(self, imagem):
        try:
            nova = Imagem((self.altura, self.largura))
            nova = self + imagem
            return nova
        except Exception as e:
            raise Exception(e.args)

    def subtracao(self, imagem):
        try:
            nova = Imagem((self.altura, self.largura))
            nova = self - imagem
            return nova
        except Exception as e:
            raise Exception(e.args)

    def multiplicacao(self, imagem):
        try:
            nova = Imagem((self.altura, self.largura))
            nova = self * imagem
            return nova
        except Exception as e:
            raise Exception(e.args)

    def divisao(self, imagem):
        try:
            nova = Imagem((self.altura, self.largura))
            nova = self / imagem
            return nova
        except Exception as e:
            raise Exception(e.args)

    def combinacaoMenor(self, imagem, imagem1, imagem2):
        if self.altura != imagem.altura and self.largura != imagem.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes')
        else:
            nova = Imagem((self.altura, self.largura))
            for y in range(self.altura):
                for x in range(self.largura):
                    r, g, b = imagem1.img.getpixel((y, x))
                    r1, g1, b1 = imagem2.img.getpixel((y, x))
                    if r < r1:
                        nova[y][x] = self.img.getpixel((y, x))
                    else:
                        nova[y][x] = imagem.img.getpixel((y, x))

            return nova

    def combinacaoMaior(self, imagem, imagem1, imagem2):
        if self.altura != imagem.altura and self.largura != imagem.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes')
        else:
            nova = Imagem((self.altura, self.largura))
            for y in range(self.altura):
                for x in range(self.largura):
                    r, g, b = imagem1.img.getpixel((y, x))
                    r1, g1, b1 = imagem2.img.getpixel((y, x))
                    if r > r1:
                        nova[y][x] = self.img.getpixel((y, x))
                    else:
                        nova[y][x] = imagem.img.getpixel((y, x))

            return nova

    def combinacaoLinear(self, imagem, alpha = 0.5):
        if self.altura != imagem.altura and self.largura != imagem.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes')
        else:
            nova = Imagem((self.altura, self.largura))
            for y in range(self.altura):
                for x in range(self.largura):
                    r, g, b = self.img.getpixel((y, x))
                    r1, g1, b1 = imagem.img.getpixel((y, x))
                    r *= alpha
                    g *= alpha
                    b *= alpha
                    r1 *= (1 - alpha)
                    g1 *= (1 - alpha)
                    b1 *= (1 - alpha)
                    nova[y][x] = (r + r1, g + g1, b + b1)

            return nova
    
    def combinacaoSigmoide(self, imagem, metodo = 1, lmb = 0.1):
        if self.altura != imagem.altura and self.largura != imagem.largura:
            raise Exception('Ambas imagens devem ter as mesmas dimensoes')
        else:
            nova = Imagem((self.altura, self.largura))
            L = 1

            #Sigmoide em x
            if metodo == 1: 
                yCentral = self.altura // 2

                for y in range(self.altura):
                    for x in range(self.largura):
                        alpha = L / (1 + (math.e ** (-lmb * (y - yCentral))))
                        r, g, b = self.img.getpixel((y, x))
                        r1, g1, b1 = imagem.img.getpixel((y, x))
                        r *= alpha
                        g *= alpha
                        b *= alpha
                        r1 *= (1 - alpha)
                        g1 *= (1 - alpha)
                        b1 *= (1 - alpha)
                        nova[y][x] = (r + r1, g + g1, b + b1)

            #Sigmóide em y
            else:
                xCentral = self.largura // 2

                for y in range(self.altura):
                    for x in range(self.largura):
                        alpha = L / (1 + (math.e ** (-lmb * (x - xCentral))))
                        r, g, b = self.img.getpixel((y, x))
                        r1, g1, b1 = imagem.img.getpixel((y, x))
                        r *= alpha
                        g *= alpha
                        b *= alpha
                        r1 *= (1 - alpha)
                        g1 *= (1 - alpha)
                        b1 *= (1 - alpha)
                        nova[y][x] = (r + r1, g + g1, b + b1)

            return nova

    def gaussXY(x, y, sigma):
        fator = (1 / (2 * math.pi * (sigma**2)))
        g = fator * math.exp((-(x**2 + y**2)) / (2 * sigma * sigma))
        return g

    def suavizacao(self, metodo = 'media', raio = 1, imagem = None):
        if metodo == 'media':
            a = np.full((raio*2 + 1, raio*2 + 1), 1.0)
            a *= 1/((raio*2 + 1)**2)
            img1 = self.convolucao(a)
            nova = self.getFromArray(img1)

            return nova
        elif metodo == 'gaausiana':
            #gerar mascara
            sigma = 1
            result = np.zeros((raio*2 + 1, raio*2 + 1))
            
            for x in range(-raio, raio+1):
                for y in range(-raio, raio+1):
                    result[x+raio][y+raio] = Imagem.gaussXY(x, y, sigma)

            
            result = result / sum(sum(result))

            img1 = self.convolucao(result)
            nova = self.getFromArray(img1)

            return nova
        elif metodo == 'mediana':
            nova = Imagem((self.altura, self.largura))

            for y in range(self.altura):
                for x in range(self.largura):
                    mr = []
                    mg = []
                    mb = []
                    for i in range(max(0,y-raio), min(self.altura,y+raio+1)):
                        for j in range(max(0,x-raio), min(self.largura,x+raio+1)):
                            r, g, b = self.img.getpixel((i, j))
                            mr.append(r)
                            mg.append(g)
                            mb.append(b)
                    
                    nova[y][x] = (int(np.median(mr)), int(np.median(mg)), int(np.median(mb)))
            return nova
        elif metodo == 'conservativa':
            nova = Imagem((self.altura, self.largura))

            for y in range(self.altura):
                for x in range(self.largura):
                    maior = []
                    menor = []
                    for i in range(max(0,y-raio), min(self.altura,y+raio+1)):
                        for j in range(max(0,x-raio), min(self.largura,x+raio+1)):
                            r, g, b = imagem.img.getpixel((i, j))
                            maior.append((r, i, j))
                            menor.append((r, i, j))
                    
                    maior.sort()
                    maior.reverse()
                    menor.sort()
                    r, i, j = maior[0]
                    r, i1, j1 = menor[0]
                    if i == y and j == x:
                        r, i, j = maior[1]
                        nova[y][x] = self.img.getpixel((i, j))
                    elif i1 == y and j1 == x:
                        r, i1, j1 = menor[1]
                        nova[y][x] = self.img.getpixel((i1, j1))
                    else:
                        nova[y][x] = self.img.getpixel((y, x))
            return nova
    def espaciais(self, metodo = 'erosao', raio = 1):
        if metodo == 'erosao' or metodo == 'dilatacao':
            nova = Imagem((self.altura, self.largura))

            for y in range(self.altura):
                for x in range(self.largura):
                    mr = []
                    mg = []
                    mb = []
                    for i in range(max(0,y-raio), min(self.altura,y+raio+1)):
                        for j in range(max(0,x-raio), min(self.largura,x+raio+1)):
                            r, g, b = self.img.getpixel((i, j))
                            mr.append(r)
                            mg.append(g)
                            mb.append(b)
                    
                    if metodo == 'erosao':
                        nova[y][x] = (max(mr), max(mg), max(mb))
                    else:
                        nova[y][x] = (min(mr), min(mg), min(mb))

            return nova
        
        elif metodo == 'vidro1':
            nova = Imagem((self.altura, self.largura))

            for y in range(self.altura):
                for x in range(self.largura):
                    mr = []
                    for i in range(max(0,y-raio), min(self.altura,y+raio+1)):
                        for j in range(max(0,x-raio), min(self.largura,x+raio+1)):
                            mr.append(self.img.getpixel((i, j)))

                    nova[y][x] = random.choice(mr)

            return nova

        elif metodo == 'vidro2':
            nova = Imagem((self.altura, self.largura))

            for y in range(self.altura):
                for x in range(self.largura):
                    mr = []
                    for i in range(max(0,y-raio), min(self.altura,y+raio+1)):
                        for j in range(max(0,x-raio), min(self.largura,x+raio+1)):
                            #r, g, b = self.img.getpixel((i, j))
                            mr.append((i, j))

                    a, b = random.choice(mr)
                    aux = self.img.getpixel((y, x))
                    nova[y][x] = self.img.getpixel((a, b))
                    nova[a][b] = aux
            
            return nova
        elif metodo == 'pixelizacao':
            nova = Imagem((self.altura, self.largura))

            for y in range(0, self.altura, raio):
                for x in range(0, self.largura, raio):
                    mr = []
                    mg = []
                    mb = []
                    for i in range(y, min(self.altura,y+raio)):
                        for j in range(x, min(self.largura,x+raio)):
                            r, g, b = self.img.getpixel((i, j))
                            mr.append(r)
                            mg.append(g)
                            mb.append(b)
                    for i in range(y, min(self.altura,y+raio)):
                        for j in range(x, min(self.largura,x+raio)):
                            nova[i][j] = (sum(mr)//len(mr), sum(mg)//len(mg), sum(mb)//len(mb))
            
            return nova

    def frequencia(self, metodo, raio = 127.0, ordem = 8, raio2 = 10.0):
        nova = Imagem((self.altura, self.largura))

        imgFreq = fftn(self.arr())
        imgFreq = fftshift(imgFreq)
        u0 = self.altura // 2
        v0 = self.largura // 2

        for i in range(self.altura):
            for j in range(self.largura):
                dist = math.sqrt((i - u0) ** 2 + (j - v0) ** 2)

                #Pra não ocorrer divisão por zero no butterworth passa alta
                if dist == 0.0 and metodo == 'butterworthPA':
                    dist += 0.000001

                if metodo == 'butterworthPB':
                    imgFreq[i][j][0] *= 1 / (1 + ((dist / raio) ** (2 * ordem)))
                    imgFreq[i][j][1] *= 1 / (1 + ((dist / raio) ** (2 * ordem)))
                    imgFreq[i][j][2] *= 1 / (1 + ((dist / raio) ** (2 * ordem)))
                elif metodo == 'butterworthPA':
                    imgFreq[i][j][0] *= 1 / (1 + ((raio / dist) ** (2 * ordem)))
                    imgFreq[i][j][1] *= 1 / (1 + ((raio / dist) ** (2 * ordem)))
                    imgFreq[i][j][2] *= 1 / (1 + ((raio / dist) ** (2 * ordem)))
                elif metodo == 'passa-baixa':
                    if dist > raio:
                        imgFreq[i][j] = (0, 0, 0)
                elif metodo == 'passa-alta':
                    if dist <= raio:
                        imgFreq[i][j] = (0, 0, 0)
                else:
                    #passa-faixa
                    if dist < min(raio, raio2) or dist > max(raio, raio2):
                        imgFreq[i][j] = (0, 0, 0)

        imgFreq = ifftshift(imgFreq)
        imgFreq = ifftn(imgFreq)


        #Voltar a imagem pro domínio do espaço
        for i in range(self.altura):
            for j in range(self.largura):
                nova[i][j] = (imgFreq[i][j][0], imgFreq[i][j][1], imgFreq[i][j][2])

        return nova

    def limiarizacao(self, metodo):
        #Passo 1 (Estimativa inicial pro limiar T)
        Tmin = 256; Tmax = -1
        nova = Imagem((self.altura, self.largura))
        for i in range(self.altura):
            for j in range(self.largura):
                r, g, b = self.img.getpixel((i, j))
                #Luminosity
                intensidade = 0.299 * r + 0.587 * g + 0.114 * b
                if intensidade < Tmax:
                    Tmin = intensidade
                if intensidade > Tmax:
                    Tmax = intensidade
        T = (Tmax + Tmin) // 2
        #Passo 2, 3, e 4 
        u1 = 0.0; u2 = 0.0; n1 = 0; n2 = 0; nIteracoes = 0; deltaT = 1; Tant = 0
        while abs(Tant - T) > deltaT:
            for i in range(self.altura):
                for j in range(self.largura):
                    r, g, b = self.img.getpixel((i, j))
                    #Luminosity
                    intensidade = 0.299 * r + 0.587 * g + 0.114 * b
                    if intensidade <= T:
                        u1 += intensidade
                        n1 += 1
                    else:
                        u2 += intensidade
                        n2 += 1
            u1 = u1 / n1
            u2 = u2 / n2
            nIteracoes += 1
            Tant = T
            T = (u1 + u2) // 2
            u1 = 0.0; u2 = 0.0; n1 = 0; n2 = 0

        #Passo 5 (nova Imagem)
        for i in range(self.altura):
            for j in range(self.largura):
                r, g, b = self.img.getpixel((i, j))
                #Luminosity
                intensidade = 0.299 * r + 0.587 * g + 0.114 * b
                if intensidade >= T:
                    nova[i][j] = (0, 0, 0)
                else:
                    nova[i][j] = (255, 255, 255)

        return nova



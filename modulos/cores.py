# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:29:50 2017

@author: marcos
"""

from sklearn.cluster import KMeans
from sklearn.utils import shuffle

from classes.imagem import Imagem

import numpy as np

def mudaCor(img, metodo='average', nTons=256):
    nova = Imagem((img.altura, img.largura))

    mSepia = []
    mSepia.append([0.393, 0.349, 0.272])
    mSepia.append([0.769, 0.686, 0.534])
    mSepia.append([0.189, 0.168, 0.131])

    for x in range(img.largura):
        for y in range(img.altura):
            r,g,b = img[y][x]
            if metodo == 'average':
                avg = (r + g + b) / 3.0
                nova[y][x] = (avg, avg, avg)
            elif metodo == 'r':
                nova[y][x] = (r,r,r)
            elif metodo == 'inv':
                nova[y][x] = (255-r, 255-g, 255-b)
            elif metodo == 'min':
                minimo = min(r, g, b)
                nova[y][x] = (minimo, minimo, minimo)
            elif metodo == 'max':
                maximo = max(r, g, b)
                nova[y][x] = (maximo, maximo, maximo)
            elif metodo == 'lightness':
                light = (max(r, b, g) + min (r, g, b)) / 2
                nova[y][x] = (light, light, light)
            elif metodo == 'luminosity':
                luminosity = 0.299*r + 0.587*g + 0.114*b
                nova[y][x] = (luminosity, luminosity, luminosity)
            elif metodo == 'g':
                nova[y][x] = (g, g, g)
            elif metodo == 'b':
                nova[y][x] = (b, b, b)
            elif metodo == 'sepia':
                for i in range(0,3):
                    soma = 0
                    for j in range(0,3):
                        if j == 0:
                            soma += r*mSepia[j][i]
                        elif j == 1:
                            soma += g*mSepia[j][i]
                        else:
                            soma += b*mSepia[j][i]
                    if i == 0:
                        somaR = soma
                    elif i ==1:
                        somaG = soma
                    else:
                        somaB = soma
                nova[y][x] = (somaR, somaG, somaB)
            else:
                nova[y][x] = (r,g,b)
    
    return nova

def balanco(img, ar, ag, ab):
    nova = Imagem((img.altura, img.largura))

    for y in range(img.altura):
        for x in range(img.largura):
            r,g,b = img[y][x]
            R = int(ar*r)
            G = int(ar*g)
            B = int(ar*b)
            nova[y][x] = (R,G,B)

    return nova

def binaria(img, metodo='padrao', vLimiar=64):
    nova = img.copia()
    if metodo == 'padrao':
        dados = img.arrLin()
        paleta = [[0,0,0], [255,255,255]]
        nClusters = 2
        amostraAleatoria = shuffle(dados, random_state=0)[:1000]
        km = KMeans(nClusters).fit(amostraAleatoria)
        labels = km.predict(dados)
        for x,label in enumerate(labels):
            i = x // img.largura
            j = x % img.largura
            r,g,b = paleta[label]
            nova[i][j] = (r,g,b)

    elif metodo == 'limiar':
        nova = mudaCor(img, 'luminosity')
        for y in range(nova.altura):
            for x in range(nova.largura):
                r,g,b = nova[y][x]
                if r > vLimiar:
                    r = 255
                else:
                    r = 0
                if g > vLimiar:
                    g = 255
                else:
                    g = 0
                if b > vLimiar:
                    b = 255
                else:
                    b = 0
                nova[y][x] = (r,g,b)

    return nova

def propaga(tup, fator):
    r,g,b = tup
    return (r + fator, g + fator, b + fator)

# Atkinson Dithering
def atkinson(img):
    nova = mudaCor(img, 'luminosity')

    for y in range(img.altura):
        for x in range(img.largura):
            r = nova[y][x][0]

            if r > 255//2:
                nova[y][x] = (255, 255, 255)
            else:
                nova[y][x] = (0, 0, 0)
            
            quantErro = r - nova[y][x][0]

            if x + 1 < img.largura:
                nova[y][x+1] = propaga(nova[y][x+1], quantErro * 1/8)
                if y + 1 < img.altura:
                    nova[y+1][x+1] = propaga(nova[y+1][x+1], quantErro * 1/8)
            if x + 2 < img.largura:
                nova[y][x+2] = propaga(nova[y][x+2], quantErro * 1/8)
            if y + 1 < img.altura:
                if x - 1 >= 0:
                    nova[y+1][x-1] = propaga(nova[y+1][x-1], quantErro * 1/8)
                nova[y+1][x] = propaga(nova[y+1][x], quantErro * 1/8)
            if y + 2 < img.altura:
                nova[y+2][x] = propaga(nova[y+2][x], quantErro * 1/8)

    return nova

# Floyd-Steinberg Dithering
def floyd(img):
    nova = mudaCor(img, 'luminosity')

    for y in range(img.altura):
        for x in range(img.largura):
            r,g,b = nova[y][x]
            if r >= 255//2:
                nova[y][x] = (255, 255, 255)
            else:
                nova[y][x] = (0, 0, 0)
            quantErro = r - nova[y][x][0]

            if x+1 < img.largura:
                nova[y][x+1] = propaga(nova[y][x+1], quantErro * 7/16)
            if y+1 < img.altura:
                if x-1 >= 0:
                    nova[y+1][x-1] = propaga(nova[y+1][x-1], quantErro * 3/16)
                nova[y+1][x] = propaga(nova[y+1][x], quantErro * 5/16)
                if x+1 < img.largura:
                    nova[y+1][x+1] = propaga(nova[y+1][x+1], quantErro * 1/16)

    return nova

# Ordered Dithering com matriz de Bayer
def bayer(img, metodo=2):
    if metodo == 2:
        matriz = np.array([[0,60], [45, 110]])
        dim = matriz.shape[0]
        
        nova = Imagem((img.altura, img.largura))

        nova2 = mudaCor(img, 'luminosity')

        for y in range(img.altura):
            for x in range(img.largura):
                r,g,b = img[y][x]
                Y, X, Z = nova2[y][x]

                if Y > matriz[y % dim][x % dim]:
                    nova[y][x] = (255, 255, 255)
                else:
                    nova[y][x] = (0, 0, 0)

        return nova
    else:
        matriz = np.array([[167,200,230,216,181], [94, 72,193,242,232], [36,52,222,167,200], [181,126,210,94,72], [232,153,111,36,52]])
        dim = matriz.shape[0]
        
        nova = Imagem((img.altura, img.largura))

        nova2 = mudaCor(img, 'luminosity')

        for y in range(img.altura):
            for x in range(img.largura):
                r,g,b = img[y][x]
                Y, X, Z = nova2[y][x]

                if Y > matriz[y % dim][x % dim]:
                    nova[y][x] = (255, 255, 255)
                else:
                    nova[y][x] = (0, 0, 0)

        return nova

#Ajuste de brilho e contraste
def brilhoContraste(img, brilho=0.0, contraste=1.0):
    nova = Imagem((img.altura, img.largura))
    
    for y in range(img.altura):
        for x in range(img.largura):
            r,g,b = img[y][x]
            nova[y][x] = (contraste*r + brilho, contraste*g + brilho, contraste*b + brilho)

    return nova

#Alargamento de contraste
def alargamentoContraste(img):
    i = 0
    nova = Imagem((img.altura, img.largura))
    vMax, xMax, yMax = Imagem.maximo(img)
    vMin, xMin, yMin = Imagem.minimo(img)
    
    for y in range(img.altura):
        for x in range (img.largura):
            
            r, g, b = img[y][x]
            novoR = round((255/(vMax[0] - vMin[0]))*(r - vMin[0]))
            novoG = round((255/(vMax[1] - vMin[1]))*(g - vMin[1]))
            novoB = round((255/(vMax[2] - vMin[2]))*(b - vMin[2]))
            nova[y][x] = (novoR, novoG, novoB)
             
    return nova

def find_closest(A, target):
    idx = A.searchsorted(target)
    idx = np.clip(idx, 1, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left < right - target
    return idx

def quantizacaoCores(img, metodo, intervalos):
    nova = Imagem((img.altura, img.largura))
    if metodo == 'prob':
        hr, hg, hb = img.histogramas()

        hr = hr / (img.altura * img.largura)
        hg = hg / (img.altura * img.largura)
        hb = hb / (img.altura * img.largura)

        d, d1, d2 = img.cdf(hr, hg, hb)

        val = np.array([find_closest(d, (i + 1) / intervalos) for i in range(intervalos)])
        val1 = np.array([find_closest(d1, (i + 1) / intervalos) for i in range(intervalos)])
        val2 = np.array([find_closest(d2, (i + 1) / intervalos) for i in range(intervalos)])
    else:
        val = np.array([i / (intervalos-1) * 255 for i in range(intervalos)])

    for y in range(img.altura):
        for x in range(img.largura):
            r, g, b = img[y][x]
            if metodo == 'prob':
                nova[y][x] = (val[find_closest(val, r)], val1[find_closest(val1, g)], val2[find_closest(val2, b)])
            else:
                nova[y][x] = (val[find_closest(val, r)], val[find_closest(val, g)], val[find_closest(val, b)])

    return nova
    

def salPimenta(img, porcentagem=0.01, proporcao=0.5):
    #fazer nova receber uma img
    nova = Imagem((img.altura, img.largura))
    nova = img

    tam = round((img.altura * img.largura) * porcentagem)

    sal = round(tam * proporcao)
    pimenta = round(tam * (1.0 - proporcao))

    #Problema de arredondamento
    if sal + pimenta < tam:
        pimenta += tam - (sal + pimenta)
    elif sal + pimenta > tam:
        pimenta -= (sal + pimenta) - tam

    y = np.random.randint(img.altura, size=tam)
    x = np.random.randint(img.largura, size=tam)

    for i, j in zip(y, x):
        v = np.random.randint(2, size=1)
        #Sal, senão, pimenta
        a = int(i)
        b = int(j)
        if v[0] == 0:
            if sal > 0:
                nova[a][b] = (255, 255, 255)
                sal -= 1
            elif pimenta > 0:
                nova[a][b] = (0, 0, 0)
                pimenta -= 1
        elif pimenta > 0:
            nova[a][b] = (0, 0, 0)
            pimenta -= 1
        elif sal > 0:
            nova[a][b] = (255, 255, 255)
            sal -= 1
    
    return nova

def ruidoGaausiano(img, m = 0.15):
    nova = Imagem((img.altura, img.largura))

    distribuicao = np.random.normal(0, 1, (img.altura, img.largura, 3))

    for y in range(img.altura):
        for x in range (img.largura):
            r, g, b = img[y][x]
            
            r1 = round(r + distribuicao[y][x][0] * r * m)
            g1 = round(g + distribuicao[y][x][1] * g * m)
            b1 = round(b + distribuicao[y][x][2] * b * m)

            nova[y][x] = (r1, g1, b1)
    
    return nova







# -*- coding: utf-8 -*-
__author__ = 'Joaquin Alvarez'

class Cotizacion:

    def __init__(self, Valor, Id_Empresa, Hora, Porcentaje, Actualizacion):
        self.Valor = Valor
        self.Id_Empresa = Id_Empresa
        self.Hora = Hora
        self.Porcentaje = Porcentaje
        self.Actualizacion = Actualizacion

    def toDBCollection(self):
        return {
            "Valor":self.Valor,
            "Id_Empresa":self.Id_Empresa,
            "Hora": self.Hora,
            "Porcentaje":self.Porcentaje,
            "Actualizacion":self.Actualizacion
        }

    def __str__(self):
        return "Id_Empresa: %s - Valor: %f - Hora: %s - Porcentaje: %f - Actualizacion: %s" \
               %(self.Id_Empresa, self.Valor, self.Hora, self.Porcentaje, self.Actualizacion)
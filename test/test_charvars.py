"""
Unit tests for various types of character variable.
"""
import os
import tempfile
import unittest
import cdlparser
import numpy as np
import netCDF4 as nc4

#---------------------------------------------------------------------------------------------------
class TestCharVars(unittest.TestCase) :
#---------------------------------------------------------------------------------------------------
   def setUp(self) :
      cdltext = r"""netcdf charvars {
         dimensions:
            nreg = 3 ;
            namelen = 10 ;
            rec = 2 ;
            code = 3 ;
            codelen = 4 ;
         variables:
            char letter ;
            int regcodes(nreg) ;
               regcodes:long_name = "region codes" ;
            char regions(nreg, namelen) ;
               regions:long_name = "region names" ;
            char digits(namelen) ;
               digits:long_name = "decimal digits" ;
            int sampleid(rec) ;
               sampleid:long_name = "sample id" ;
            char dna_code(rec, code, codelen) ;
               dna_code:long_name = "DNA code" ;
         // global attributes
            :comment = "a cast of unholy characters" ;
         data:
            regcodes = 1, 2, 3 ;
            regions = "Europe", "Americas", "Asia" ;
            digits = "0123456789" ;
            letter = "X" ;
            sampleid = 1, 2 ;
            dna_code = "ACTG", "ACGG", "ATGC", "CTGA", "GCTA", "TGCA";
      }"""
      parser = cdlparser.CDL3Parser()
      self.tmpfile = tempfile.mkstemp(suffix='.nc')[1]
      self.dataset = parser.parse_text(cdltext, ncfile=self.tmpfile)

   def tearDown(self) :
      if os.path.exists(self.tmpfile) : os.remove(self.tmpfile)

   def test_scalar_variables(self) :
      var = self.dataset.variables['letter']
      self.assertTrue(var[:] == b"X")

   def test_non_scalar_variables(self) :
      var = self.dataset.variables['regcodes']
      self.assertTrue(var.long_name == "region codes")
      self.assertTrue(var.shape == (3,))
      data = var[:]
      expected = np.array([1,2,3], dtype=np.int32)
      expected.shape = (3,)
      self.assertTrue(np.array_equal(data, expected))

      var = self.dataset.variables['regions']
      self.assertTrue(var.long_name == "region names")
      self.assertTrue(var.shape == (3,10))
      data = var[:]
      data = nc4.chartostring(data)
      self.assertTrue(data[0].startswith(b"Europe"))
      self.assertTrue(data[1].startswith(b"Americas"))
      self.assertTrue(data[2].startswith(b"Asia"))

      var = self.dataset.variables['digits']
      self.assertTrue(var.long_name == "decimal digits")
      self.assertTrue(var.shape == (10,))
      data = var[:]
      data = nc4.chartostring(data)
      self.assertTrue(data == b"0123456789")

      var = self.dataset.variables['dna_code']
      self.assertTrue(var.long_name == "DNA code")
      self.assertTrue(var.shape == (2,3,4))
      data = var[:]
      sample = nc4.chartostring(data[0])
      self.assertTrue(sample[0] == b"ACTG")
      self.assertTrue(sample[1] == b"ACGG")
      self.assertTrue(sample[2] == b"ATGC")
      sample = nc4.chartostring(data[1])
      self.assertTrue(sample[0] == b"CTGA")
      self.assertTrue(sample[1] == b"GCTA")
      self.assertTrue(sample[2] == b"TGCA")

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
#---------------------------------------------------------------------------------------------------
   unittest.main()

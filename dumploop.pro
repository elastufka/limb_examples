pro dumbloop

fits=file_search('data/dat_files/*.fits')     
for i=0,4 do begin 
   fit_results=spex_read_fit_results(fits[i])
   print, fit_results.spex_summ_params
   endfor

end

;+
;; Reading fit results from file data/dat_files/xrs2010307.fits
;; MRDFITS: Null image, NAXIS=0
;; MRDFITS: Binary table.  31 columns by  1 rows.
;; MRDFITS: Binary table.  3 columns by  225 rows.
;;      0.332954      1.54828      1.00000     0.329826      1.55374      1.00000
;; Reading fit results from file data/dat_files/xrs2011264.fits
;; MRDFITS: Null image, NAXIS=0
;; MRDFITS: Binary table.  31 columns by  1 rows.
;; MRDFITS: Binary table.  3 columns by  225 rows.
;;     0.0962120      1.36158      1.00000   0.00720967      1.39426      1.00000
;; Reading fit results from file data/dat_files/xrs2011268.fits
;; MRDFITS: Null image, NAXIS=0
;; MRDFITS: Binary table.  31 columns by  1 rows.
;; MRDFITS: Binary table.  3 columns by  225 rows.
;;     0.0424884      1.15524      1.00000     0.103312      1.15747      1.00000
;; Reading fit results from file data/dat_files/xrs2012083.fits
;; MRDFITS: Null image, NAXIS=0
;; MRDFITS: Binary table.  31 columns by  1 rows.
;; MRDFITS: Binary table.  3 columns by  225 rows.
;;     0.0343647      1.23061      1.00000     0.137608      1.23161      1.00000
;; Reading fit results from file data/dat_files/xrs2012146.fits
;; MRDFITS: Null image, NAXIS=0
;; MRDFITS: Binary table.  31 columns by  1 rows.
;; MRDFITS: Binary table.  3 columns by  225 rows.
;; 0.147669      1.38657      1.00000     0.148966      1.37839      1.00000
;-

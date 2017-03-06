
PRO ospex_auto_limb58_thermal,ind,stop=stop,silent=silent,peak_only=peak_only,do_again=do_again,do_high=do_high,no_e0=no_e0

; .r ospex_auto_limb58_thermal
; ospex_auto_limb58_thermal,13,/peak_only,/stop
; for i=0,57 do ospex_auto_limb58_thermal,i,/peak_only,/silent
; help,findfile('/disks/sundrop/home/krucker/hsi_data/limb/ospex/ospex_limb_summ_peak_*.dat')
; help,findfile('/disks/sundrop/home/krucker/hsi_data/limb/ospex/ospex_limb_summ_total_*.dat')
; help,findfile('/disks/sundrop/home/krucker/hsi_data/limb/ospex/ospex_limb_summ_peak_*.dat')
; help,findfile('/disks/sundrop/home/krucker/hsi_data/limb/ospex/ospex_limb_summ_total_*.dat')
; ftotal=findfile('/disks/sundrop/home/krucker/hsi_data/limb/ospex/ospex_limb_summ_total_*.dat')
; fpeak=findfile('/disks/sundrop/home/krucker/hsi_data/limb/ospex/ospex_limb_summ_peak_*.dat')
; for i=0,n_elements(ftotal)-1 do print,ftotal(i),fpeak(i)

dd0='/disks/sundrop/home/krucker/hsi_data/ospex_data/data/'
spfile=findfile(dd0+'hsi_spectrum_*_limb.fits')
srmfile=findfile(dd0+'hsi_srm_*_limb.fits')
restore,'spd06_good_event_58.dat'
dd='/disks/sundrop/home/krucker/hsi_data/limb/images/'
dds='/disks/sundrop/home/krucker/hsi_data/limb/ospex/'
frange='limb_2images_ranges_'+good_dddd(ind)+'.dat'
restore,dd+frange,/verbose
this_bkg=pp.tr_bkg
this_tr=pp.tr_flare
er_high=pp.er(*,1)
de=er_high(1)-er_high(0)
er_high0=[er_high(1)-de/2.,er_high(1)]
;er_high0=[er_high(1),er_high(1)+5]

this_file=spfile(ind)
this_dfile=srmfile(ind)

o=ospex(/no_gui)
o->set, spex_specfile=this_file
o->set, spex_drmfile=this_dfile
o->set, spex_eband=get_edge_products([3,12,18,25,40,100],/edges_2)
o->set,spex_bk_time_interval=this_bkg

o->set, fit_function='vth+vth+vth'

add_name='total_'
if keyword_set(peak_only) then begin
   ;get maximum witin this_tr
   data=o->getdata(class='spex_data')
   eaxis=o->getaxis(/ct_energy)
   taxis=o->getaxis(/mean)
   elist=where( (eaxis ge min(er_high)) AND (eaxis le max(er_high)) )
   phigh=total(data.data(elist,*),1)
   tlist=where( (taxis ge min(this_tr)) AND (taxis le max(this_tr)) )
   phigh=phigh(tlist)
   this_max=max(phigh,this_max_ind)
   this_tr0=this_tr
   this_tr1=taxis(tlist(this_max_ind))+[-8.,8.]
this_tr=[max([this_tr0(0),this_tr1(0)]),min([this_tr0(1),this_tr1(1)])]
   add_name='peak_'
endif

o->set, spex_fit_time_interval=this_tr
if keyword_set(silent) then begin
o->set,spex_autoplot_enable=0,spex_fit_progbar=0,spex_fitcomp_plot_resid=0
   ;o->set,OSPEX_NOINTERACTIVE=1
endif else begin
   o->set, spex_autoplot_enable=1
endelse
o->set,spex_fit_manual=0

if keyword_set(stop) then stop

;first fit thermal only
o-> set, fit_comp_free_mask= [1,1,0, 0,0,0, 0,0,0]
o->set, spex_erange= [6.0D, 12.D]
e_low_end=6.
o-> set, fit_comp_params= [1.0, 2.0, 1.0, 0.0, 4.0, 1.0, 0.0, 6., 1.0]
o->set,spex_fit_manual=0
o->dofit, /all

;if fit bad, do it again with better guess
param_now=o->get(/fit_comp_params)
if ((param_now(0) le 1e-8) or (param_now(1) le 0.5) or (keyword_set(do_again))) then begin
  o-> set, fit_comp_free_mask= [1,1,0, 0,0,0, 0,0,0]
    p0=o->get(/spex_summ)
    ddee=p0.spex_summ_energy(1,*)-p0.spex_summ_energy(0,*)
eeee=reform((p0.spex_summ_energy(1,*)+p0.spex_summ_energy(0,*))/2.)
    ffff=p0.SPEX_SUMM_CT_RATE(*)
    pppp=ffff/p0.spex_summ_area/ddee
    ;plot_oo,eeee,pppp,yrange=[min(pppp),max(pppp)*100]
;oplot,eeee,f_vth(p0.spex_summ_energy,[1.,2,1])*p0.SPEX_SUMM_CONV
    elist=where( (eeee ge 6) AND (eeee le 12) )
    f12=pppp(elist)
    th12=f_vth(p0.spex_summ_energy,[1.,2,1])*p0.SPEX_SUMM_CONV
    t12=th12(elist)
    this_em=average(f12/t12)
;oplot,eeee,f_vth(p0.spex_summ_energy,[this_em,2,1])*p0.SPEX_SUMM_CONV
  o-> set, fit_comp_params= [this_em, 2.0, 1.0, 0.0, 2.0, 1.0, 0.0, 6., 1.0]
  o->set,spex_fit_manual=0
  o->dofit, /all
endif
;if fit still bad, do it again at higher energy
param_now=o->get(/fit_comp_params)
if ((param_now(0) le 1e-8) or (param_now(1) le 0.5) or (keyword_set(do_high))) then begin
  o-> set, fit_comp_free_mask= [1,1,0,0,0,0,0,0,0]
  o->set, spex_erange= [12.0D, 15.D]
  e_low_end=12.
    p0=o->get(/spex_summ)
    ddee=p0.spex_summ_energy(1,*)-p0.spex_summ_energy(0,*)
eeee=reform((p0.spex_summ_energy(1,*)+p0.spex_summ_energy(0,*))/2.)
    ffff=p0.SPEX_SUMM_CT_RATE(*)
    pppp=ffff/p0.spex_summ_area/ddee
    ;plot_oo,eeee,pppp,yrange=[min(pppp),max(pppp)*100]
;oplot,eeee,f_vth(p0.spex_summ_energy,[1.,2,1])*p0.SPEX_SUMM_CONV
    elist=where( (eeee ge 12) AND (eeee le 15) )
    f12=pppp(elist)
    th12=f_vth(p0.spex_summ_energy,[1.,2,1])*p0.SPEX_SUMM_CONV
    t12=th12(elist)
    this_em=average(f12/t12)
    ;th12=f_vth([12,15],[1.,2,1])*p0.SPEX_SUMM_CONV
;oplot,eeee,f_vth(p0.spex_summ_energy,[this_em,2,1])*p0.SPEX_SUMM_CONV
  o-> set, fit_comp_params= [this_em, 2.0, 1.0, 0.0, 2.0, 1.0, 0.0, 6., 1.0]
  o->set,spex_fit_manual=0
  o->dofit, /all
endif
if keyword_set(stop) then stop

;assume t2 is twice the lower temperature and fit EM3 only
o->set,fit_comp_free_mask= [0,0,0,1,0,0,0,0,0]
o->set,spex_erange=er_high0
th_fit=o->get(/fit_comp_params)
th_fit(3)=th_fit(0)/100.
th_fit(4)=2*th_fit(1)
th_fit(5)=1
o->set,fit_comp_params=th_fit
o->set,spex_fit_manual=0
o->dofit, /all
;now also fit EM2
o->set,fit_comp_free_mask= [0,0,0,1,1,0,0,0,0]
o->dofit, /all

;total range
  o->set,fit_comp_free_mask= [1,1,0,1,1,0,0,0,0]
  o->set,spex_erange=[e_low_end,er_high0(1)+5.]
  o->set,spex_fit_manual=0
  o->dofit, /all


;save result
sfilename='ospex_limb_summ_thermal_'+add_name+good_dddd(ind)+'.dat'
p0=o->get(/spex_summ)
save,p0,filename=dds+sfilename

if keyword_set(stop) then stop

END




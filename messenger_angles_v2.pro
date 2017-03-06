function get_messenger_angle,filename,outfilename,plot=plot
;gets the angles between Mercury and Earth for the flares in Dennis's messenger list

    ; read in the data
    restore, filename ;this is a .sav file of the data object. Restored sturcture is named 'flare_list'
    len = size(flare_list.id,/dim)
    for i=0,len[0]-1 do begin
       flare_list.angle[i]=messenger_flare_angle([-200.,200.], strmid(flare_list.Datetimes.Messenger_datetimes[i],0,10)) ;1,12
       print,flare_list.angle[i]
    endfor
    save, flare_list, filename = outfilename

    if plot ne 0 then begin
        cghistoplot, flare_list.angle, nbins=18 ,/fill, yran=[0,30], xran=[-180,180],ytitle='Number of events',xtitle='Angle between Messenger and the Sun'
    endif

end

function calc_goes_class,filename,outfilename,plot=plot

;calculate the GOES class for each flare, using the largest of EM1 and
;EM2

    ;read in the data
    restore,filename
    len = size(flare_list.id,/dim)
    goesnum = fltarr(len[0])
    
    for i=0,len[0]-1 do begin
        TMKelvin = flare_list.flare_properties.Messenger_T*11.6045 ;convert from keV to MK
        goes_fluxes,TMKelvin[i],flare_list.flare_properties.Messenger_EM1[i],flong,fshort,sat=15, abund=1
        goesnum[i]=fshort
        flare_list.flare_properties.Messenger_GOES[i]=goes_value2class(fshort)
    endfor
    print, goesnum
    if plot ne 0 then begin
        cghistoplot, alog10(goesnum), nbins=7 ,/fill, yran=[0,250], xran=[-10,0],ytitle='Number of events',xtitle='log flux, W/m^2'
     endif
    
    save, flare_list, filename = outfilename
end

;function format_csv,fl, outfilename ;j/k idl is stupid, why the 8 column limit???
;fl.datetimes.RHESSI_datetimes,fl.datetimes.obs_start_time,fl.datetimes.obs_end_time,fl.flare_properties.messenger_T,fl.flare_properties.messenger_EM1,fl.flare_properties.messenger_goes,fl.flare_properties.messenger_total_counts,fl.flare_properties.rhessi_goes,fl.flare_properties.rhessi_total_counts,fl.flare_properties.source_vis,fl.data_properties.messenger_data_path,fl.data_properties.rhessi_data_path,fl.data_properties.xrs_files,fl.data_properties.ql_images,fl.data_properties.rhessi_browser_urls,fl.data_properties.csv_name,fl.angle,fl.notes]
;    headers =['ID','Messenger_datetimes','RHESSI_datetimes','Obs_start_time','Obs_end_time','Messenger_T','Messenger_EM1','Messenger_GOES','Messenger_total_counts','RHESSI_GOES','RHESSI_total_counts','source_vis','Messenger_data_path','RHESSI_data_path','XRS_files','QL_images','RHESSI_browser_urls','csv_name','Angle','Notes'] 
;    write_csv, outfilename, fl.ID,fl.datetimes.messenger_datetimes,fl.datetimes.RHESSI_datetimes,fl.datetimes.obs_start_time,fl.datetimes.obs_end_time,fl.flare_properties.messenger_T,fl.flare_properties.messenger_EM1,fl.flare_properties.messenger_goes,fl.flare_properties.messenger_total_counts;,header=headers 
;end

;result=get_messenger_angle('list_observed_obj.sav','list_observed_ang.sav', plot=1)
;nresult=calc_goes_class('list_observed_ang.sav','list_observed_goes.sav', plot=1)
;foo = format_csv(flare_list, 'list_observed_goes.csv')
;end

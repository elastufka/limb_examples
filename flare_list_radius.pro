time_range = ['2004/08/20 00:00', '2011/01/28 00:00']  
 
    ;load the original flare list  
    flare_list_orig_obj=hsi_flare_list( obs_time_interval = time_range )  
    flare_list_orig=flare_list_orig_obj -> getdata()  
 
    dim_orig_flare = n_elements(flare_list_orig)  
 
    print, 'Orig Flare List: Found ', dim_orig_flare  
 
    x_orig = flare_list_orig.position(0)  
    y_orig = flare_list_orig.position(1)  

    ;first just find any flares that might be occulted
    radius_orig = sqrt( x_orig^2 + y_orig^2 )  
    radius_sun= get_rb0p(flare_list_orig.start_time, /radius)

    limb=where(radius_orig/radius_sun gt 1.0)
    limb_flare_list=flare_list_orig[limb]
    print, size(limb_flare_list)

    ;then pick the ones above a certain energy threshold
    
    ;listlen = size(limb_flare_list,/dim)
    ;for i=0, listlen[0]-1 do begin
    ;    elen = size(limb_flare_list[i].energy_range_found,/dim)
    ;    if (isa(limbgt12) eq 1) and (limb_flare_list[i].energy_hi[elen[0]-1] gt 11) then begin
    ;        limbgt12 = [limbgt12, limb_flare_list[i]]
    ;     endif else begin
    ;        if limb_flare_list[i].energy_hi[elen[0]-1] gt 11 then limbgt12 = limb_flare_list[i]
    ;     endelse
    ;endfor
    ;print, size(limbgt12) ;looks like this is the wrong parameter to search ... it returns the same thing!
    ;limb_flare_list = limbgt12


    ; let's choose data quality <2
    ;listlen = size(limb_flare_list,/dim)
    ;for i=0, listlen[0]-1 do begin
    ;    if limb_flare_list[i] -> Get(flag_name = 'DATA_QUALITY' ) lt 3 then begin
    ;        limbgt12 = [limbgt12, limb_flare_list[i]]
    ;     endif else begin
    ;        if limb_flare_list[i].energy_hu[elen[0]-1] gt 11 then limbgt12 = limb_flare_list[i]
    ;     endelse
    ;endfor

    ; and those with a quicklook image to make our job easier
    ;listlen = size(limb_flare_list,/dim)
    ;for i=0, listlen[0]-1 do begin
    ;    elen = size(limb_flare_list[i].energy_range_found,/dim)
    ;    if (isa(limbgt12) eq 1) and (limb_flare_list[i].energy_hi[elen[0]-1] gt 11) then begin
    ;        limbgt12 = [limbgt12, limb_flare_list[i]]
    ;     endif else begin
    ;        if limb_flare_list[i].energy_hu[elen[0]-1] gt 11 then limbgt12 = limb_flare_list[i]
    ;     endelse
    ;endfor

    ;save the list for comparison to Messenger (or STEREO?)

    ;do I first want to compare Messenger GOES class to STEREO GOES class for a baseline?
end

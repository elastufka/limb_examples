;pro get_flare_angles

;gets the angles between Mercury and Earth for the flares in Dennis's messenger list

; read in the data
filename = '/Users/wheatley/Documents/Solar/MiSolFA/statistics/messenger_list.csv'
flare_list = read_csv(filename)

angle=dblarr(656)

for i=0,655 do begin
   splitstring = strsplit(flare_list.field2[i],'/',/extract)
                                ;mm/dd/yy -> yy/mm/dd
                                ;89/12/15, 22:00:15.234
   tstring = strsplit(flare_list.field3[i],' ',/extract)
   strings = splitstring[2]+'/'+splitstring[0]+'/'+splitstring[1]+ ' '+tstring[0]
   angle[i]=messenger_flare_angle([-200.,200.], strings)
   print, tstring,strings,angle[i]
endfor

anglest={Angle:angle}
newst = {Index:flare_list.field1, Date:flare_list.field2, Star_Time:flare_list.field3, End_Time:flare_list.field4, Duration:flare_list.field5, Angle:angle}
write_csv, 'messenger_angles.csv',newst

end

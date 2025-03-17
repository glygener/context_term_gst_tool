from __future__ import division,print_function
import time,re,sys,os
import pandas as pd

import random,operator
from collections import OrderedDict
from bson.son import SON
from bson.codec_options import CodecOptions
from bson import ObjectId
import string
from nltk.tokenize import word_tokenize
import json

def get_entityFormat(entityType,eachAA):
    eachEntity = {}
    eachEntity["entityType"] = entityType
    eachEntity["charStart"] = eachAA[0][1]
    eachEntity["charEnd"] = eachAA[0][1] + len(eachAA[0][0]) - 1 #eachAA[0][2]-1
    eachEntity["sentenceIndex"] = eachAA[1]
    eachEntity["entityText"] = eachAA[0][0]
    eachEntity["source"] = "SiteDetectorTool"

    return eachEntity


def furtherProcessing(allTypesInAbstract,pmid):

    # row = str(pmid) + "\t" + str(allTypesInAbstract) + "\t" + str(aasiteThatIsGene) + "\t" + isInMedline2018
    pmidJSON = {}
    AA_entities = []
    for aatype,listOfAA in allTypesInAbstract.items():
        eachEntity = {}
        if aatype == "type1" or aatype == "type2":
            for eachAA in listOfAA:
                eachEntity = get_entityFormat("AminoAcid",eachAA)
                AA_entities.append(eachEntity)

        elif aatype == "typeSeq1" or aatype == "typeSeq2":
            for eachAA in listOfAA:
                eachEntity = get_entityFormat("SiteSequence",eachAA)
                AA_entities.append(eachEntity)

        elif aatype == "typeSeq3" or aatype == "typeSeq4":
            continue

        elif aatype == "typeSite":
            continue
            # for eachAA in listOfAA:
            #     if eachAA not in aasiteThatIsGene:
            #         eachEntity = get_entityFormat("Sites",eachAA)
            #         AA_entities.append(eachEntity)

        elif aatype == "typeDomain":
            continue
            # for eachAA in listOfAA:
            #     if eachAA not in aasiteThatIsGene:
            #         eachEntity = get_entityFormat("Domains",eachAA)
            #         AA_entities.append(eachEntity)

        else:
            for eachAA in listOfAA:
                eachEntity = get_entityFormat("SpecificSite",eachAA)
                AA_entities.append(eachEntity)

    if AA_entities:
        pmidJSON["docId"] = pmid
        pmidJSON["entity"] = AA_entities
        # print(json.dumps(pmidJSON,indent=4))

    return pmidJSON

def consolidate_types_together(old_dict,new_dict,senIndex):
    for key,value in old_dict.items():
        if key not in new_dict.keys():
            new_dict[key] = []
        for each in value:
            new_dict[key].append((each,senIndex))

    return new_dict


def extract_site_sequence(type_dict_withOffset,senText,charStart,charEnd,typeName,typeSeqName):
    extract_site_sequence_dict = {}
    if typeName in type_dict_withOffset:
        if len(type_dict_withOffset[typeName]) == 1:
            return {}
        else:
            listOfType3 = type_dict_withOffset[typeName]
            for i in range(len(listOfType3)):
                for j in range(len(listOfType3)):
                    if i != j:
                        sequenceText = listOfType3[i][0] + "-" + listOfType3[j][0]
                        if not senText.find(sequenceText) == -1 or listOfType3[j][1] == listOfType3[i][2]+1:
                            # senIndex =
                            siteSeqCharStart = listOfType3[i][1]
                            siteSeqCharEnd = listOfType3[j][2]
                            if typeSeqName in extract_site_sequence_dict:
                                extract_site_sequence_dict[typeSeqName].append((sequenceText,siteSeqCharStart,siteSeqCharEnd))
                            else:
                                extract_site_sequence_dict[typeSeqName] = [(sequenceText,siteSeqCharStart,siteSeqCharEnd)]


    return extract_site_sequence_dict

def spans(txt,start):
    tokens=tokenize_includingHyphen(txt)
    offset = 0
    for index,token in enumerate(tokens):
        offset = txt.find(token, offset)
        yield index, token, offset+start, offset+len(token)+start
        offset += len(token)

def get_spanInfo_forEachToken(senText,sen_charStart):
    list_token_withSpan = []
    for spanInfo in spans(senText,sen_charStart):
        list_token_withSpan.append(spanInfo)

    return list_token_withSpan

def get_offset_for_typeDict_inEachSen(type_dict,senText,sen_charStart,sen_charEnd):
    finalDict = {}
    list_token_withSpanInfo = get_spanInfo_forEachToken(senText,sen_charStart) #(6, u'structure', 1534, 1543)
    # print(list_token_withSpanInfo)
    for key,value in type_dict.items():
        # key = type3_1
        finalDict[key] = []
        for eachSiteWithTokenStart in value:
            newSite = []
            #{'type3_1': [(u'N13', 7, 8)]} -: eachSiteWithTokenStart: (AAsiteString,StartToken,EndToken(or beginning of nextT))
            site_charStart = 0
            site_charEnd = 0
            # print(eachSiteWithTokenStart)
            for everyTokenAndSpan in list_token_withSpanInfo:
                # everyTokenAndSpan = (6, u'structure', 1534, 1543)
                # eachSiteWithTokenStart: (AAsiteString,StartToken,EndToken)
                if everyTokenAndSpan[0] == eachSiteWithTokenStart[1]: # eachSiteWithTokenStart[1] is startPos of siteToken
                    site_charStart = everyTokenAndSpan[2]
                else:
                    if everyTokenAndSpan[0] == eachSiteWithTokenStart[2]:
                        #Check if endtoken for site is not end of sentence : then get position right before the start of next token
                        site_charEnd = everyTokenAndSpan[2]
                    elif eachSiteWithTokenStart[2] > list_token_withSpanInfo[-1][0]:
                        site_charEnd = list_token_withSpanInfo[-1][3]


            if site_charStart == 0 and site_charEnd == 0:
                print("Something Wrong")
                print(type_dict,key,value)
                print(eachSiteWithTokenStart)
                exit(0)

            siteText = senText[site_charStart-sen_charStart:site_charEnd-sen_charStart]

            # print(siteText)
            '''
            1.if siteText[-1] == ')' and not re.search("\(",siteText): Example: Ser32)
            2.if senText[site_charEnd-sen_charStart] == ")" and re.search("\(",siteText): Example: Ser(32 --> and ) is the next char: increase charEnd to include end bracket
            3. if space at end: remove space and decrease charEnd
            '''
            if siteText[-1] == ')' and siteText.find("(") == -1:
                siteText = senText[site_charStart-sen_charStart:site_charEnd-sen_charStart-1]
                site_charEnd = site_charEnd-1

            elif siteText.find("(") != -1 and catch_index_error(senText,site_charEnd-sen_charStart) and senText[site_charEnd-sen_charStart] == ")":
                siteText = senText[site_charStart-sen_charStart:site_charEnd-sen_charStart+1]
                site_charEnd = site_charEnd+1



            elif siteText[-1] == ' ':
                # Example: siteText = "Ser32 "
                siteText = senText[site_charStart-sen_charStart:site_charEnd-sen_charStart-1]
                site_charEnd = site_charEnd-1

            elif siteText[0] == ' ':
                # Example: siteText = " Ser32"
                siteText = senText[site_charStart-sen_charStart+1:site_charEnd-sen_charStart]
                site_charStart = site_charStart+1

            elif siteText[-1] == ' ' and siteText[0] == ' ':
                # Example: " Ser32 "
                siteText = senText[site_charStart-sen_charStart+1:site_charEnd-sen_charStart-1]
                site_charStart = site_charStart+1
                site_charEnd = site_charEnd-1

            newSite.append((siteText,site_charStart,site_charEnd))
            finalDict[key] = finalDict[key] + newSite

    return finalDict

def NO_aa_BUTResidue_FOLLOWEDBYSite(senText,listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern):
    # type_sequence = listOfTokensInSentence[tokenPos:tokenPos+1+1]
    type_sequence = listOfTokensInSentence[startPos:tokenPos+1+1]
    '''
    tokenPos contains "residue"
    tokenPos+1 may contain "residue 35"
    '''
    if not catch_index_error(listOfTokensInSentence,tokenPos+1) == 'null':
        next_next_token = listOfTokensInSentence[tokenPos+1]
        '''
        next_next_token contains the next word after "residue".
        For example:
            If "residue 35"
                next_next_token = 35
            Or, if "residue at 35"
                next_next_token = at
            Or, if "residue location 35"
                next_next_token = location

            {type4}: residue at location 35   --> Type SpecificSite
            {type4}: residue positions 35 and 48   --> Type SpecificSite
            {type5}:   --> Type SpecificSite
                a. residue 35
                b. residues 2, 4 and 123
                c. residues (2 and 123)


                location_token,posOfLastLoc = get_location(listOfTokensInSentence,assumed_positionOfFirstNumber-1,location_pattern)

            if location_token:
                # print "-->"," ".join(location_token)
                # type_sequence = listOfTokensInSentence[tokenPos:posOfLastLoc+1]
                type_sequence = listOfTokensInSentence[startPos:posOfLastLoc+1]
                type_dict = add_to_dict(typeName,type_sequence,type_dict,startPos)
                tokenPos = posOfLastLoc+1
        '''
        if re.match("\\b(in|at)\\b",next_next_token): #serine residue[s] in(at)
            tokenPos,type_dict = aa_followedByResidue_followedByInAt(listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern,type_sequence)
        elif re.match("\\b(location|position)[s]?\\b",next_next_token): #serine residue[s] location(position)
            '''
            Since we don't check if the next token is a number, assumed_positionOfFirstNumber is the exact position of the starting number
            Hence, assumed_positionOfFirstNumber won't be decreased when retrieving the list of numbers
            '''
            assumed_positionOfFirstNumber = tokenPos+3
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type4",location_pattern)

        elif location_pattern.match(next_next_token): #serine residue[s] 35
            assumed_positionOfFirstNumber = tokenPos+2
            '''
            tokenPos+2 contain 35 from "serine residue 35"
            During checking of location in assign_type4_type5, assumed_positionOfFirstNumber is decreased by 1; but the returned tokenPos is tokenPos+3, because we want to set the token to the word after the last location for the next iteration
            '''
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type5",location_pattern)

        elif re.match("[^A-Za-z0-9]",next_next_token) and catch_index_error(listOfTokensInSentence,tokenPos+3) != 'null' and location_pattern.match(listOfTokensInSentence[tokenPos+3]):
            #serine residue[s] (35, 37 and 42)
            assumed_positionOfFirstNumber = tokenPos+4
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type5",location_pattern)

        else:
            tokenPos = tokenPos + 1
    else:
        tokenPos = tokenPos + 1
    return tokenPos,type_dict

def singleLetter_aa_tokens(startPos,tokenPos,listOfTokensInSentence,type_dict,location_pattern):
    '''
    Example:
        S-35 : Token:S
        S(35): Token: S
    '''
    type_sequence = [listOfTokensInSentence[startPos]]
    # print(type_sequence)
    # print(listOfTokensInSentence[tokenPos])
    # print(listOfTokensInSentence[tokenPos+2])
    # print(listOfTokensInSentence[tokenPos+3])
    # print(listOfTokensInSentence[tokenPos+4])
    if not catch_index_error(listOfTokensInSentence,tokenPos+1) == 'null': # Some location or word after single letter
        next_Token = listOfTokensInSentence[tokenPos+1]
        if next_Token == "-":
            # Example: S-35
            tokenPos = tokenPos + 1
            next_Token = listOfTokensInSentence[tokenPos+1]

            location_token,posOfLastLoc = get_location(listOfTokensInSentence,tokenPos+1,location_pattern)
            if location_token:
                # type_sequence = listOfTokensInSentence[tokenPos:posOfLastLoc+1]
                type_sequence = listOfTokensInSentence[startPos:posOfLastLoc+1]
                # type_dict = add_to_dict("type3",type_sequence,type_dict,tokenPos)
                type_dict = add_to_dict("type3_1",type_sequence,type_dict,startPos)
                tokenPos = posOfLastLoc+1

        elif next_Token == "(":
            '''
            S: TokenPos
            S(:TokenPos+1 --> next_Token
            S(35:TokenPos+2
            S(35):TokenPos+3
            '''
            # locationAfterParanthesisStart = tokenPos+2
            # tokenAfterlocation = tokenPos+3
            if not catch_index_error(listOfTokensInSentence,tokenPos+2) == 'null' and not catch_index_error(listOfTokensInSentence,tokenPos+3) == 'null':
                if listOfTokensInSentence[tokenPos+3] == ')':

                    # tokenPos = tokenPos+1 # increased to (
                    location_token,posOfLastLoc = get_location(listOfTokensInSentence,tokenPos+2,location_pattern)
                    if location_token:
                        # type_sequence = listOfTokensInSentence[tokenPos:posOfLastLoc+1]
                        type_sequence = listOfTokensInSentence[startPos:posOfLastLoc+1]
                        # type_dict = add_to_dict("type3",type_sequence,type_dict,tokenPos)
                        type_dict = add_to_dict("type3_1",type_sequence,type_dict,startPos)
                        tokenPos = posOfLastLoc+1
                    else:
                        tokenPos = tokenPos+4
                else:
                    tokenPos = tokenPos + 1
            else:
                tokenPos = tokenPos + 1

        else:
            tokenPos = tokenPos + 1

    else:
        tokenPos = tokenPos + 1
    return tokenPos,type_dict

def aa_followedByinAt_thenMaybeSite(senText,listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern):
    # type_sequence = listOfTokensInSentence[tokenPos:tokenPos+1+1]
    # type_sequence = listOfTokensInSentence[startPos:tokenPos+1+1]
    '''
    tokenPos contains "serine"
    tokenPos+1 will contain "serine at"
    tokenPos+2 may contain "serine at 35"
    '''
    if catch_index_error(listOfTokensInSentence,tokenPos+2) == 'null':
        '''
        If the last 2 words of the sentence are "serine at", no further processing --> Simply return type 1
        {type1}: serine --> Type AminoAcid
        '''
        type_sequence = listOfTokensInSentence[startPos:tokenPos+1]
        type_dict = add_to_dict("type1",type_sequence,type_dict,startPos)
        tokenPos = tokenPos+1

    else:
        next_next_token = listOfTokensInSentence[tokenPos+2]
        '''
        next_next_token contains the next word after "serine at".
        For example:
            If "serine at 35"
                next_next_token = 35
            Or, if "serine at location 35"
                next_next_token = at

            {type4}: serine at location 35   --> Type SpecificSite
            {type4}: serine at positions 35 and 48   --> Type SpecificSite
            {type3}: serine at 35 and 48   --> Type SpecificSite
        '''
        if re.match("\\b(location|position)[s]?\\b",next_next_token): #serine residue[s] location(position)
            '''
            Since we don't check if the next token is a number, assumed_positionOfFirstNumber is the exact position of the starting number
            Hence, assumed_positionOfFirstNumber won't be decreased when retrieving the list of numbers
            '''
            assumed_positionOfFirstNumber = tokenPos+3
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type4",location_pattern)

        elif location_pattern.match(next_next_token): #serine residue[s] 35
            assumed_positionOfFirstNumber = tokenPos+3
            '''
            tokenPos+2 contain 35 from "serine residue 35"
            During checking of location in assign_type4_type5, assumed_positionOfFirstNumber is decreased by 1; but the returned tokenPos is tokenPos+3, because we want to set the token to the word after the last location for the next iteration
            '''
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type3",location_pattern)

        else:
            type_sequence = listOfTokensInSentence[startPos:tokenPos+1]
            type_dict = add_to_dict("type1",type_sequence,type_dict,startPos)
            tokenPos = tokenPos+1

    return tokenPos,type_dict

def assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,typeName,location_pattern):
    if typeName == "type4":
        location_token,posOfLastLoc = get_location(listOfTokensInSentence,assumed_positionOfFirstNumber,location_pattern)
    if typeName == "type3" or typeName == "type5":
        '''
        We already tested (before coming to this function) if the assumed_positionOfFirstNumber is the token after the number
        i.e we test if location_pattern.match(listOfTokensInSentence[tokenPos+2])
        and then we want to check for the next token. So assumed_positionOfFirstNumber = tokenPos+3
        Hence when retrieving the list of numbers we start from assumed_positionOfFirstNumber-1
        '''
        location_token,posOfLastLoc = get_location(listOfTokensInSentence,assumed_positionOfFirstNumber-1,location_pattern)

    if location_token:
        # print "-->"," ".join(location_token)
        # type_sequence = listOfTokensInSentence[tokenPos:posOfLastLoc+1]
        type_sequence = listOfTokensInSentence[startPos:posOfLastLoc+1]
        type_dict = add_to_dict(typeName,type_sequence,type_dict,startPos)
        tokenPos = posOfLastLoc+1
    else:
        # type_sequence = listOfTokensInSentence[tokenPos:assumed_positionOfFirstNumber]
        type_sequence = listOfTokensInSentence[startPos:assumed_positionOfFirstNumber]
        type_dict = add_to_dict(typeName,type_sequence,type_dict,startPos)
        tokenPos = assumed_positionOfFirstNumber
    return tokenPos,type_dict

def aa_followedByResidue_followedByInAt(listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern,type_sequence):
    '''
    For example:
        If "serine residue at 35"
            tokenPos = serine
            next_next_token = tokenPos+2 = at
            next_next_next_token = tokenPos+3 = 35

        Or, if "serine residue at locations 35, 48 and 123"
            next_next_token = tokenPos+2 = at
            next_next_next_token = tokenPos+3 = locations

            tokenPos+4 = 35
    {type4}: serine residue at location 35   --> Type SpecificSite
    {type2}: serine residue --> Type AminoAcid
    '''
    if catch_index_error(listOfTokensInSentence,tokenPos+3) != 'null':
        next_next_next_token = listOfTokensInSentence[tokenPos+3]
        if re.match("\\b(location|position)[s]?\\b",next_next_next_token): #serine residue[s] in(at) location(position)
            assumed_positionOfFirstNumber = tokenPos+4
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type4",location_pattern)

        else:
            type_dict = add_to_dict("type2",type_sequence,type_dict,startPos)
            tokenPos = tokenPos+2

    return tokenPos,type_dict

def aa_followedByResidue_thenMaybeSite(senText,listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern):
    # type_sequence = listOfTokensInSentence[tokenPos:tokenPos+1+1]
    type_sequence = listOfTokensInSentence[startPos:tokenPos+1+1]
    '''
    tokenPos contains "serine"
    tokenPos+1 will contain "serine residue"
    tokenPos+2 may contain "serine residue 35"
    '''
    if catch_index_error(listOfTokensInSentence,tokenPos+2) == 'null':
        '''
        If the last 2 words of the sentence are "serine residue", no further processing --> Simply return type 2
        {type2}: serine residue --> Type AminoAcid
        '''
        type_dict = add_to_dict("type2",type_sequence,type_dict,startPos)
        tokenPos = tokenPos+2

    else:
        next_next_token = listOfTokensInSentence[tokenPos+2]
        '''
        next_next_token contains the next word after "serine residue".
        For example:
            If "serine residue 35"
                next_next_token = 35
            Or, if "serine residue at 35"
                next_next_token = at
            Or, if "serine residue location 35"
                next_next_token = location

            {type2}: serine residue --> Type AminoAcid
            {type4}: serine residue at location 35   --> Type SpecificSite
            {type4}: serine residue positions 35 and 48   --> Type SpecificSite
            {type5}:   --> Type SpecificSite
                a. serine residue 35
                b. serine residues 2, 4 and 123
                c. serine residues (2 and 123)
        '''
        if re.match("\\b(in|at)\\b",next_next_token): #serine residue[s] in(at)
            tokenPos,type_dict = aa_followedByResidue_followedByInAt(listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern,type_sequence)
        elif re.match("\\b(location|position)[s]?\\b",next_next_token): #serine residue[s] location(position)
            '''
            Since we don't check if the next token is a number, assumed_positionOfFirstNumber is the exact position of the starting number
            Hence, assumed_positionOfFirstNumber won't be decreased when retrieving the list of numbers
            '''
            assumed_positionOfFirstNumber = tokenPos+3
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type4",location_pattern)

        elif location_pattern.match(next_next_token): #serine residue[s] 35
            assumed_positionOfFirstNumber = tokenPos+3
            '''
            tokenPos+2 contain 35 from "serine residue 35"
            During checking of location in assign_type4_type5, assumed_positionOfFirstNumber is decreased by 1; but the returned tokenPos is tokenPos+3, because we want to set the token to the word after the last location for the next iteration
            '''
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type5",location_pattern)

        elif re.match("[^A-Za-z0-9]",next_next_token) and catch_index_error(listOfTokensInSentence,tokenPos+3) != 'null' and location_pattern.match(listOfTokensInSentence[tokenPos+3]):
            #serine residue[s] (35, 37 and 42)
            assumed_positionOfFirstNumber = tokenPos+4
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type5",location_pattern)

        else:
            type_dict = add_to_dict("type2",type_sequence,type_dict,startPos)
            tokenPos = tokenPos+2

    return tokenPos,type_dict

def get_location(listOfTokensInSentence,tokenPos,location_pattern):
    '''
    This function will return the a series of site locations and the token position of the last site location.
    For eg: If "serine residue 35,43 and 123" -- > will return [35,43,123] and the position of 123
    '''

    locationList = []

    locPatt_Last = 0

    while (tokenPos < len(listOfTokensInSentence)):
        # print(listOfTokensInSentence)
        if listOfTokensInSentence[tokenPos] == '':
            tokenPos = tokenPos + 1
            # u'(', u'Asn', '-', u'117', u'', ',', u'', u'', '-', u'184', u'', ',', u'', u'and', u'', '-', u'448', u')
            # continue
        elif location_pattern.match(listOfTokensInSentence[tokenPos]):
            locationList.append(listOfTokensInSentence[tokenPos])
            locPatt_Last = tokenPos
            tokenPos = tokenPos + 1


        elif re.match(",|-|and|or",listOfTokensInSentence[tokenPos]):
            tokenPos = tokenPos + 1

        else:
             tokenPos = locPatt_Last
             break
    return locationList,tokenPos


def aa_site_maybeFollowedByresidue(listOfTokensInSentence,startPos,tokenPos,location_pattern,type_dict):
    '''
    3. {type3}:   --> Type SpecificSite
        a. serine 35
        ...
        f. serine 35, 48 and 91
        g. ser-23, -45, and -98
    6. {type6}:   --> Type SpecificSite
        a. serine 35 residue
        b. serine 51 or 48 residues
    '''
    location_token,posOfLastLoc = get_location(listOfTokensInSentence,tokenPos+1,location_pattern)
    # print(location_token,posOfLastLoc)
    if location_token:
        # print "-->"," ".join(location_token)
        # if residue follows ser 35 put it as type 6
        if catch_index_error(listOfTokensInSentence,posOfLastLoc+1) != 'null' and re.match("\\bresidue[s]?\\b",listOfTokensInSentence[posOfLastLoc+1]):
            # type_sequence = listOfTokensInSentence[tokenPos:posOfLastLoc+1+1]
            type_sequence = listOfTokensInSentence[startPos:posOfLastLoc+1+1]
            type_dict = add_to_dict("type6",type_sequence,type_dict,startPos)
            tokenPos = posOfLastLoc+2

        else:
            # type_sequence = listOfTokensInSentence[tokenPos:posOfLastLoc+1]
            type_sequence = listOfTokensInSentence[startPos:posOfLastLoc+1]
            type_dict = add_to_dict("type3",type_sequence,type_dict,startPos)
            tokenPos = posOfLastLoc+1
    else:
        # type_sequence = listOfTokensInSentence[tokenPos:tokenPos+1+1]
        type_sequence = listOfTokensInSentence[startPos:tokenPos+1+1]
        type_dict = add_to_dict("type3",type_sequence,type_dict,startPos)
        tokenPos = tokenPos+2

    return tokenPos,type_dict

def add_to_dict(key,type_sequence,type_dict,startingPos):

    endingPos = startingPos + len(type_sequence)
    if key not in type_dict.keys():
        type_dict[key] = [(" ".join(type_sequence),startingPos,endingPos)]
    else:
        type_dict[key].append((" ".join(type_sequence),startingPos,endingPos))

    return type_dict

def catch_index_error(listOfValue,pos):
    try:
        gotdata = listOfValue[pos]
    except (IndexError, ValueError):
        gotdata = 'null'

    return gotdata

def non_hyphenated_tokens(senText,startPos,tokenPos,listOfTokensInSentence,type_dict,location_pattern,acidType):
    # type_sequence = [listOfTokensInSentence[tokenPos]]
    # print(acidType)
    if acidType == "Not_Acid":
        type_sequence = [listOfTokensInSentence[startPos]]
    else:
        type_sequence = listOfTokensInSentence[startPos:startPos+2]
        # print("type_sequence",type_sequence)
    # startPos = tokenPos
    if catch_index_error(listOfTokensInSentence,tokenPos+1) == 'null': # Last token is Serine
        '''
        Example:
            serine
            ser
        '''
        type_dict = add_to_dict("type1",type_sequence,type_dict,tokenPos)
        tokenPos = tokenPos+1

    else: #Token is NOT the Last word
        next_Token = listOfTokensInSentence[tokenPos+1] # token after amino acid
        if next_Token == "-":
            # print(next_Token,tokenPos)
            tokenPos = tokenPos+1
            next_Token = listOfTokensInSentence[tokenPos+1]

        # next_Token was moved to after -, if - is present
        if location_pattern.match(next_Token):
            '''
            Example:
                serine 35
                ser 35 residue
            '''
            tokenPos,type_dict = aa_site_maybeFollowedByresidue(listOfTokensInSentence,startPos,tokenPos,location_pattern,type_dict)

        elif re.match("\\bresidue[s]?\\b",next_Token): #serine residue[s]
            '''
            Example:
                serine residue
                ser residues 35, 38 and 123
            '''
            tokenPos,type_dict = aa_followedByResidue_thenMaybeSite(senText,listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern)
        elif re.match("[^A-Za-z0-9]",next_Token) and catch_index_error(listOfTokensInSentence,tokenPos+2) != 'null' and location_pattern.match(listOfTokensInSentence[tokenPos+2]):
            '''
            tokenPos -> Ser
            Make sure tokenPos+1 is not the last word, example: "Ser."
            next_Token = listOfTokensInSentence[tokenPos+1]
            ser is followed by any other character other than number and letter and the location after that has the number: Example: Ser(35.) -- > ["Ser", "(", "35", ".", ")"]
            '''

            assumed_positionOfFirstNumber = tokenPos+3
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type3",location_pattern)

        elif re.match("\\b(in|at)\\b",next_Token): #serine at 35
            '''
            Example:
                serine at 35
                ser at position 35
            '''
            tokenPos,type_dict = aa_followedByinAt_thenMaybeSite(senText,listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern)

        elif re.match("\\b(location|position)[s]?\\b",next_Token):  # serine location 35
            '''
            Example:
                serine location 35
                {type4}: serine location 35   --> Type SpecificSite
            '''
            assumed_positionOfFirstNumber = tokenPos+2
            tokenPos,type_dict = assign_type3_type4_type5(listOfTokensInSentence,startPos,tokenPos,assumed_positionOfFirstNumber,type_dict,"type4",location_pattern)

        else:
            '''
            {type1}: serine --> Type AminoAcid
            '''
            # type_sequence = [listOfTokensInSentence[startPos]]
            # print(type_sequence)
            type_dict = add_to_dict("type1",type_sequence,type_dict,startPos)
            tokenPos = tokenPos+1
    return tokenPos,type_dict

def tokenize_includingHyphen(senText):
    listOfTokensInSentence = []
    tokens = word_tokenize(senText)
    for token in tokens:
        if re.search("\\-",token):
            splitTokens = re.split("-",token)
            for spTok in splitTokens[0:-1]:
                listOfTokensInSentence.append(spTok)
                listOfTokensInSentence.append("-")
            listOfTokensInSentence.append(splitTokens[-1])


        elif re.search("\\,",token):
            # print(token)
            splitTokens = re.split(",",token)
            # print(splitTokens)
            for spTok in splitTokens[0:-1]:
                listOfTokensInSentence.append(spTok)
                listOfTokensInSentence.append(",")
            listOfTokensInSentence.append(splitTokens[-1])

        elif re.search("\\/,",token):
            splitTokens = re.split("/",token)
            for spTok in splitTokens[0:-1]:
                listOfTokensInSentence.append(spTok)
                listOfTokensInSentence.append("/")
            listOfTokensInSentence.append(splitTokens[-1])

        else:
            listOfTokensInSentence.append(token)
    return listOfTokensInSentence


def match_pattern_in_sentence(senText,senIndex,pmid,amino_acid,amino_acid_letter,amino_acid_pattern,location_pattern,amino_acid_dash_location,amino_acid_endingWithAcid,aminoAcidSingleLetter_dash_location,amino_acid_dash_location_sequence,aminoAcidSingleLetter_dash_location_sequence,domain_pattern,site_pattern,stopping_pattern,punctuation_pattern,aminoAcidSingleLetter):
    # type_dict = {}
    listOfTokensInSentence = tokenize_includingHyphen(senText)
    # print(listOfTokensInSentence)
    # exit(0)
    # print(senText)
    type_dict = get_types_fromEachSen_forWholeAbvAminoAcid(senText,listOfTokensInSentence,amino_acid,amino_acid_letter,amino_acid_pattern,location_pattern,amino_acid_dash_location,amino_acid_endingWithAcid,aminoAcidSingleLetter_dash_location,amino_acid_dash_location_sequence,aminoAcidSingleLetter_dash_location_sequence,domain_pattern,site_pattern,stopping_pattern,punctuation_pattern,aminoAcidSingleLetter)

    return type_dict

def get_types_fromEachSen_forWholeAbvAminoAcid(senText,listOfTokensInSentence,amino_acid,amino_acid_letter,amino_acid_pattern,location_pattern,amino_acid_dash_location,amino_acid_endingWithAcid,aminoAcidSingleLetter_dash_location,amino_acid_dash_location_sequence,aminoAcidSingleLetter_dash_location_sequence,domain_pattern,site_pattern,stopping_pattern,punctuation_pattern,aminoAcidSingleLetter):

    '''
    Hyphenated words are not tokenized
    Example:
    Pmid: 10715549
    [u'Additional', u'N-glycosylation', u'at', u'Asn', u'(', u'13', u')', u'rescues', u'the', u'human', u'LHbeta-subunit', u'from', u'disulfide-linked', u'aggregation']
    '''
    type_dict = {}
    tokenPos = 0
    # print("Entering while loop of get_types_fromEachSen_forWholeAbvAminoAcid")
    # print(listOfTokensInSentence)

    while (tokenPos < len(listOfTokensInSentence)):
        # print("TokenPos:",tokenPos)
        startPos = tokenPos
        if amino_acid_pattern.match(listOfTokensInSentence[tokenPos]):
            # print("Test 1:",listOfTokensInSentence[tokenPos])
            # serine 35; ser-35
            tokenPos,type_dict = non_hyphenated_tokens(senText,startPos,tokenPos,listOfTokensInSentence,type_dict,location_pattern,"Not_Acid")

        elif amino_acid_dash_location.match(listOfTokensInSentence[tokenPos]):
            # print("Test 2:",listOfTokensInSentence[tokenPos])
            # the name is misleading. Hyphen will be tokenized now. Hence: Only Ser34 or serine35
            tokenPos,type_dict = non_hyphenated_tokens(senText,startPos,tokenPos,listOfTokensInSentence,type_dict,location_pattern,"Not_Acid")

        elif aminoAcidSingleLetter.match(listOfTokensInSentence[tokenPos]):
            # print("Test 3:",listOfTokensInSentence[tokenPos])
            # S-35; S(35)
            tokenPos,type_dict = singleLetter_aa_tokens(startPos,tokenPos,listOfTokensInSentence,type_dict,location_pattern)

        elif aminoAcidSingleLetter_dash_location.match(listOfTokensInSentence[tokenPos]):
            # print("Test 4:",listOfTokensInSentence[tokenPos])
            # the name is misleading. Hyphen will be tokenized now. Hence: S35
            type_sequence = [listOfTokensInSentence[tokenPos]]
            type_dict = add_to_dict("type3_1",type_sequence,type_dict,tokenPos)
            tokenPos = tokenPos+1

        elif re.match(amino_acid_endingWithAcid,listOfTokensInSentence[tokenPos],re.I):
            if re.match("acid",listOfTokensInSentence[tokenPos+1],re.I):
                tokenPos = tokenPos + 1

            tokenPos,type_dict = non_hyphenated_tokens(senText,startPos,tokenPos,listOfTokensInSentence,type_dict,location_pattern,"Acid")
        elif re.match("\\bresidue[s]?\\b",listOfTokensInSentence[tokenPos]): # residue[s] 35, 38 and 123
            '''
            Example:
                residues 35, 38 and 123
            '''
            # print(listOfTokensInSentence[tokenPos])
            tokenPos,type_dict = NO_aa_BUTResidue_FOLLOWEDBYSite(senText,listOfTokensInSentence,startPos,tokenPos,type_dict,location_pattern)
            # print(tokenPos,type_dict)

        else:
            tokenPos = tokenPos+1

        startPos = tokenPos
    return type_dict

def findSitesIn_abstract(pmid, text_folder, sentence_file):
    amino_acid_letter = "(A|R|N|D|C|Q|E|G|H|I|L|K|M|F|P|S|T|W|Y|V)"
    amino_acid = "(ala|arg|asn|asp|cys|gln|glu|gly|his|ile|leu|lys|met|phe|pro|ser|thr|trp|tyr|val|alanine|arginine|asparagine|cysteine|glutamine|glycine|histidine|isoleucine|leucine|lysine|methionine|phenylalanine|proline|serine|threonine|tryptophan|tyrosine|valine)"
    amino_acid_endingWithAcid = "(aspartic|glutamic)"
    inbetween = "(-)?" # inbetween will not be found anymore because the words are being tokenized when hyphen is observed
    location = "\\d{1,4}"

    domainText = "domain|region|motif|sequence"
    articles = "a|an|the"
    conjunction = "and|or|but"
    preposition = "to|of|for|from|with"
    verb = "be|is|was"

    amino_acid_pattern = re.compile("\\b"+amino_acid+"[s]?\\b$",re.I) # regex1
    location_pattern = re.compile("\\b"+location+"\\b$",re.I) # regex2
    amino_acid_dash_location = re.compile("\\b(?:"+ amino_acid + inbetween + location + "(?![a-zA-Z/]))\\b",re.I) # regex3 #mutation
    amino_acid_dash_location_sequence = re.compile("\\b"+ amino_acid + inbetween + location + "-" + amino_acid + "?" + inbetween + location + "\\b$",re.I) # regex4

    #Single Letter Amino Acid: S35, S-35, S35-H42, Ignore: S35A
    aminoAcidSingleLetter = re.compile("\\b"+amino_acid_letter+"\\b$",re.I)
    aminoAcidSingleLetter_dash_location = re.compile("\\b(?:"+ amino_acid_letter + inbetween + location + "(?![a-zA-Z/]))\\b$",re.I) # regex5 #mutation

    aminoAcidSingleLetter_dash_location_sequence = re.compile("\\b(?:"+ amino_acid_letter + inbetween + location + "-" + amino_acid_letter + "?"+ inbetween + location + ")\\b$",re.I) # regex5

    #Domain and Sites:
    domain_pattern = re.compile("\\b"+domainText+"[s]?\\b",re.I) # regex1
    site_pattern = re.compile("\\bsite[s]?\\b",re.I) # regex2
    stopping_pattern = re.compile("\\b^(" + articles + "|" + conjunction + "|" + verb + "|" + preposition + ")$\\b",re.I)
    punctuation_pattern = re.compile("(?![a-zA-Z0-9])")

    allTypesInAbstract = {}
    #aasiteThatIsGene = []

    text_file_path = os.path.join(text_folder, "{}.txt".format(pmid))
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Read raw_doc["sentence"] from an Excel file
    #print(f"Reading sentence file: {sentence_file}")
    sentence_df = pd.read_excel(sentence_file)

    #print(f"Loaded {len(sentence_df)} sentences from the Excel file")
    #print("First few rows of sentence_df:", sentence_df.head())
    sentence_df['pmid'] = sentence_df['pmid'].astype(str)
    pmid = str(pmid)
    sentence_df = sentence_df[sentence_df['pmid'] == pmid]
    #print(f"Filtered sentences for docId {pmid}: {len(sentence_df)}")


    sentence = []
    for _, row in sentence_df.iterrows():
        sentence.append({
            "index": row["sent_index"],
            "charStart": row["charStart"],
            "charEnd": row["charEnd"]
        })

    raw_doc = {"text": text, "sentence": sentence}

    #raw_doc = fromDBCollection.find_one({"docId":pmid})
    if raw_doc and "text" in raw_doc and "sentence" in raw_doc:
        singleLetter_type3 = {"type3_1":[]}
        title_abstract = raw_doc["text"]
        sentence = raw_doc["sentence"]
        for senInfo in sentence:
            senText = title_abstract[senInfo["charStart"]:senInfo["charEnd"]]
            senIndex = senInfo["index"]
            # print("senIndex:",senIndex)
            # print(senText)
            type_dict = match_pattern_in_sentence(senText,senIndex,pmid,amino_acid,amino_acid_letter,amino_acid_pattern,location_pattern,amino_acid_dash_location,amino_acid_endingWithAcid,aminoAcidSingleLetter_dash_location,amino_acid_dash_location_sequence,aminoAcidSingleLetter_dash_location_sequence,domain_pattern,site_pattern,stopping_pattern,punctuation_pattern,aminoAcidSingleLetter)
            # print()

            # print("--> ",type_dict)

            type_dict_withOffset = get_offset_for_typeDict_inEachSen(type_dict,senText,senInfo["charStart"],senInfo["charEnd"])

            seq1_dict = extract_site_sequence(type_dict_withOffset,senText,senInfo["charStart"],senInfo["charEnd"],"type3","typeSeq1")
            seq2_dict = extract_site_sequence(type_dict_withOffset,senText,senInfo["charStart"],senInfo["charEnd"],"type3_1","typeSeq2")
            # print("==: ",type_dict_withOffset)
            # print()


            allTypesInAbstract = consolidate_types_together(type_dict_withOffset,allTypesInAbstract,senIndex)
            allTypesInAbstract = consolidate_types_together(seq1_dict,allTypesInAbstract,senIndex)
            allTypesInAbstract = consolidate_types_together(seq2_dict,allTypesInAbstract,senIndex)

        if "type3_1" in allTypesInAbstract:
            singleLetter_type3["type3_1"] = allTypesInAbstract["type3_1"]

        #aasiteThatIsGene = check_if_site_isGene(singleLetter_type3["type3_1"],toDBCollection,pmid)
        # print(allTypesInAbstract)
    # exit(0)
        pmidJSON = furtherProcessing(allTypesInAbstract,pmid)
    else:
        pmidJSON = furtherProcessing(allTypesInAbstract,pmid)

    return pmidJSON


def run_forPmidFile(text_folder,sentence_file):
    #pmidList = pd.read_csv(pmidFile).iloc[:,0].tolist() # : for all rows, 0 for col1

    pmidList = [f.split('.')[0] for f in os.listdir(text_folder) if f.endswith('.txt')]
    # print(pmidList)
    pmidResults = []
    for index,pmid in enumerate(pmidList):
        #print(index,":",pmid)
        pmidJSON = findSitesIn_abstract(str(pmid),text_folder,sentence_file)
        pmidResults.append(pmidJSON) 
        print(pmidResults)
    return pmidResults


if __name__ == "__main__":
    '''
    pmidFile = sys.argv[1]
    dbF = sys.argv[2]
    dbT = sys.argv[3]
    colF = sys.argv[4]
    colT = sys.argv[5]
    '''

    
    base_dir = os.path.dirname(os.path.abspath(__file__))

    output_text_dir = os.path.join(base_dir, '/app/abstract_version/abstract_text')
    #pmidFile = sys.argv[1]
    text_folder = os.path.join(base_dir, '/app/abstract_version/abstract_text')
    sentence_file = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/sentences.xlsx')

    json_file_path = os.path.join(base_dir, '/app/abstract_version/Outputs_Abstract/pmid_results.json')

    converted_pmidJSONList = []
     

    '''

    #--- create database instances---
    # Environment variables
    mongodb_host = os.environ.get("MONGODB_HOST","127.0.0.1") # change to biotm2.cis.udel.edu before dockerizing
    mongodb_port = os.environ.get("MONGODB_PORT","27017")
    db_name_from = os.environ.get("DBNAME_FROM",dbF) # change database name for your own dbName
    db_name_to = os.environ.get("DBNAME_TO",dbT) # change database name for your own dbName

    fromCollectionName = os.environ.get("COLLECTION_FROM",colF)
    toCollectionName = os.environ.get("COLLECTION_TO",colT)
    # Database URI
    MONGODB_URI = 'mongodb://'+mongodb_host+':'+mongodb_port+'/'

    # Database object
    client = MongoClient(MONGODB_URI)
    opts = CodecOptions(document_class=SON)

    # Database
    dbNameFrom = client[db_name_from] # medline
    dbNameTo = client[db_name_to] # New DB: glygen

    # Collection
    fromDBCollection = dbNameFrom[fromCollectionName].with_options(codec_options=opts)
    toDBCollection = dbNameTo[toCollectionName].with_options(codec_options=opts)

    '''

    pmidJSONList = run_forPmidFile(text_folder,sentence_file)
    #pmid = "10200178"
    # print("\n\n","- "*5,pmid," - "*5,"\n\n")
    # print(pmid)
    #pmidJSON = run_forEachPmid(pmid,fromDBCollection,toDBCollection)
    #print(json.dumps(pmidJSON,indent=4))

    
    for pmidJSON in pmidJSONList:
        converted_pmidJSON = {}
        for key, value in pmidJSON.items():
            if isinstance(value, ObjectId):
                converted_pmidJSON[key] = str(value)
                print(converted_pmidJSON[key])
            else:
                converted_pmidJSON[key] = value
    
        #toDBCollection.insert_one(converted_pmidJSON)
        converted_pmidJSONList.append(converted_pmidJSON)
        print(json.dumps(converted_pmidJSON, indent=4, default = str))


    with open(json_file_path, "w") as json_file:
        json.dump(converted_pmidJSONList, json_file, indent=4, default=str)

    print(f"JSON data has been written to {json_file_path}")
    
package com.aivle0102.bigproject.controller;

import com.aivle0102.bigproject.dto.AgeGroupResult;
import com.aivle0102.bigproject.dto.MultiCountryRequest;
import com.aivle0102.bigproject.dto.PersonaBatchRequest;
import com.aivle0102.bigproject.domain.VirtualConsumer;
import com.aivle0102.bigproject.service.PersonaService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/persona")
public class PersonaController {

    private final PersonaService personaService;

    //1. ?àÏãú?ºÏóê ÎßûÎäî Íµ??Î≥??∞Î†π?Ä Top1 ÎΩëÍ∏∞
    @PostMapping("/age-group")
    public List<AgeGroupResult> getTopAgeGroups(@RequestBody MultiCountryRequest request) {
        return personaService.selectTopAgeGroups(request.getRecipe(), request.getCountries());
    }

    //2. Íµ??Î≥?Top1 ?∞Î†π?Ä??AI ?òÎ•¥?åÎÇò Í∞ÅÍ∞Å ?ùÏÑ± Î∞∞Ïπò
    @PostMapping("/batch")
    public List<VirtualConsumer> generatePersonas(@RequestBody PersonaBatchRequest request) {
        return personaService.generatePersonas(request.getRecipeSummary(), request.getTargets());
    }
}

